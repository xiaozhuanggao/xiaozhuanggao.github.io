---
title: LangGraph 实战——有状态 Agent 的正确打开方式
categories:
  - AI
tags:
  - Agent
  - LangGraph
  - LangChain
  - 框架
description: LangChain 的 Agent 是无状态的，LangGraph 引入了"图"的概念，让 Agent 能保持状态、分支、回退。
date: 2026-07-25 10:00:00
---

# LangGraph 实战——有状态 Agent 的正确打开方式

> LangChain 的 `AgentExecutor` 是无状态的——每次调用都是新的。**LangGraph 引入了"图"的概念**,让 Agent 能保持状态、分支、回退。

## 为什么需要 LangGraph

### LangChain AgentExecutor 的局限

```python
# LangChain 经典用法
agent_executor = AgentExecutor(agent=agent, tools=tools)
result = agent_executor.run("...")
```

问题:
1. **无状态**:每次调用都是新会话
2. **无法分支**:不能根据条件走不同路径
3. **无法回退**:执行错了不能撤销
4. **并行难**:多步并行需要手动管理

### LangGraph 的解决思路

把 Agent 当成"图":
- **节点**(Node):每个工具或 LLM 调用
- **边**(Edge):节点之间的转移
- **状态**(State):跨节点共享的数据

**本质是"用图论做 Agent 编排"**。

## 第一个 LangGraph 程序

### 安装

```bash
pip install langgraph langchain-openai
```

### 最简单的例子:问答 + 工具调用

```python
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool

# 1. 定义状态
class State(TypedDict):
    messages: Annotated[list, add_messages]

# 2. 定义工具
@tool
def search(query: str) -> str:
    """搜索工具"""
    return f"搜索结果:{query}"

@tool
def get_weather(city: str) -> str:
    """天气查询工具"""
    return f"{city}今天晴,28 度"

tools = [search, get_weather]
llm = ChatOpenAI(model="gpt-4o").bind_tools(tools)

# 3. 定义节点
def chatbot(state: State):
    return {"messages": [llm.invoke(state["messages"])]}

# 4. 定义路由
def should_continue(state: State):
    last_msg = state["messages"][-1]
    if last_msg.tool_calls:
        return "tools"
    return END

# 5. 工具节点
from langgraph.prebuilt import ToolNode
tool_node = ToolNode(tools)

# 6. 构建图
graph = StateGraph(State)
graph.add_node("chatbot", chatbot)
graph.add_node("tools", tool_node)

graph.add_edge(START, "chatbot")
graph.add_conditional_edges("chatbot", should_continue, ["tools", END])
graph.add_edge("tools", "chatbot")

# 7. 编译
app = graph.compile()

# 8. 运行
result = app.invoke({
    "messages": [HumanMessage(content="上海今天天气怎么样?")]
})
```

**核心概念**:
- `StateGraph`:图定义
- `add_node` / `add_edge`:节点和边
- `add_conditional_edges`:条件边(根据状态决定下一步)
- `compile()`:编译成可执行对象

## 进阶:带分支的 Agent

```python
class State(TypedDict):
    messages: Annotated[list, add_messages]
    needs_human_review: bool
    final_answer: str

# 节点 1:判断是否需要人工审核
def check_safety(state: State):
    last_msg = state["messages"][-1]
    is_safe = check_safety_with_llm(last_msg.content)
    return {"needs_human_review": not is_safe}

# 节点 2:人工审核节点(在真实环境会暂停等待人工输入)
def human_review(state: State):
    print("需要人工审核:", state["messages"][-1].content)
    # 真实场景这里会阻塞等待
    return {"final_answer": state["messages"][-1].content}

# 节点 3:直接返回
def auto_respond(state: State):
    return {"final_answer": state["messages"][-1].content}

# 图
graph = StateGraph(State)
graph.add_node("chatbot", chatbot)
graph.add_node("check_safety", check_safety)
graph.add_node("human_review", human_review)
graph.add_node("auto_respond", auto_respond)

graph.add_edge(START, "chatbot")
graph.add_edge("chatbot", "check_safety")
graph.add_conditional_edges(
    "check_safety",
    lambda s: "human" if s["needs_human_review"] else "auto",
    {"human": "human_review", "auto": "auto_respond"}
)
graph.add_edge("human_review", END)
graph.add_edge("auto_respond", END)
```

**这种"安全分支"模式**是生产 Agent 必备——**AI 不能直接面向用户,必须有审核环节**。

## 进阶:循环 + 反思

```python
class State(TypedDict):
    messages: Annotated[list, add_messages]
    code: str
    test_results: str
    iteration: int

# 生成代码
def generate_code(state: State):
    code = llm.invoke(f"写一个排序函数:{state['messages'][-1].content}")
    return {"code": code, "iteration": state["iteration"] + 1}

# 运行测试
def run_tests(state: State):
    try:
        result = execute_test(state["code"])
        return {"test_results": result}
    except Exception as e:
        return {"test_results": f"测试失败:{e}"}

# 反思
def reflect(state: State):
    reflection = llm.invoke(f"""
    代码:{state['code']}
    测试结果:{state['test_results']}
    请分析哪里有问题,如何改进。
    """)
    return {"messages": [reflection]}

# 路由:测试通过 / 继续迭代 / 超限
def should_continue(state: State):
    if "PASS" in state["test_results"]:
        return END
    if state["iteration"] >= 5:
        return END
    return "reflect"

# 构建图
graph = StateGraph(State)
graph.add_node("generate", generate_code)
graph.add_node("test", run_tests)
graph.add_node("reflect", reflect)

graph.add_edge(START, "generate")
graph.add_edge("generate", "test")
graph.add_conditional_edges("test", should_continue, {
    END: END,
    "reflect": "reflect"
})
graph.add_edge("reflect", "generate")

app = graph.compile()
```

**这就是 LangGraph 的核心优势**——**循环 + 状态共享**天然支持 Reflection 模式。

## 持久化:让 Agent 真的"有状态"

```python
from langgraph.checkpoint.memory import MemorySaver

memory = MemorySaver()
app = graph.compile(checkpointer=memory)

# 配置 thread_id
config = {"configurable": {"thread_id": "user_123"}}

# 第一次对话
app.invoke({"messages": [HumanMessage("我叫张三")]}, config)

# 第二次对话(能记住)
app.invoke({"messages": [HumanMessage("我叫什么?")]}, config)
# 输出:"你叫张三"
```

**`thread_id` 就是"会话 ID"**——同一个 ID 下,Agent 能记住所有历史。

### 持久化到数据库

```python
from langgraph.checkpoint.postgres import PostgresSaver

DB_URI = "postgresql://user:pass@localhost/agent_db"
checkpointer = PostgresSaver.from_conn_string(DB_URI)
app = graph.compile(checkpointer=checkpointer)
```

**支持 Postgres、Redis、MongoDB 等**——生产环境必备。

## Human-in-the-Loop

LangGraph **原生支持"人工介入"**:

```python
from langgraph.prebuilt import interrupt

def human_review(state: State):
    # 暂停在这里,等待人工输入
    user_input = interrupt({"code": state["code"]})
    return {"messages": [HumanMessage(user_input)]}
```

**真实生产中,这种"AI 不确定时暂停等人工"是必须的**——AI 不能 100% 自主。

## Stream 输出

```python
for chunk in app.stream({"messages": [HumanMessage("...")]}, config):
    print(chunk)
```

**Stream 模式让用户看到 Agent 的"思考过程"**——这对 UX 很重要。

支持多种 stream:
- `values`:完整状态
- `updates`:增量变化
- `events`:事件流(包括工具调用、状态变化)

## LangGraph vs LangChain Agent

| 维度 | LangChain AgentExecutor | LangGraph |
|---|---|---|
| 状态 | 无 | 有(持久化) |
| 分支 | 不支持 | 原生支持 |
| 循环 | 不支持 | 原生支持 |
| 并行 | 手动 | 原生支持 |
| 学习曲线 | 低 | 中 |
| 适用 | 简单 Agent | 复杂 Agent |

**经验法则**:
- **AgentExecutor**:原型验证、PoC
- **LangGraph**:生产系统

## 我用 LangGraph 做过的项目

### 项目 1:客服 Agent(简单版)

```python
graph = StateGraph(State)
graph.add_node("agent", call_llm)
graph.add_node("tools", ToolNode(tools))
graph.add_edge(START, "agent")
graph.add_conditional_edges("agent", should_use_tools)
graph.add_edge("tools", "agent")
```

50 行代码搞定,**生产稳定运行半年**。

### 项目 2:研究助手(Plan-and-Execute)

```python
graph = StateGraph(State)
graph.add_node("planner", planner_node)
graph.add_node("executor", executor_node)
graph.add_node("summarizer", summarizer_node)
graph.add_edge(START, "planner")
graph.add_edge("planner", "executor")
graph.add_edge("executor", "summarizer")
graph.add_edge("summarizer", END)
```

**Plan 一次生成,执行多步,最后汇总**——Plan-and-Execute 的标准实现。

### 项目 3:代码生成 Agent(Reflection)

100 行 LangGraph 代码,实现:
- 生成代码
- 运行测试
- 失败反思
- 重试
- 最多 5 次迭代

**首轮成功率 60%,反思后 90%**。

## 写在最后

LangGraph 是**当前最有生产力的 Agent 框架**——它把"图"这个抽象引入 Agent 编排,**解决了 LangChain AgentExecutor 的根本局限**。

如果你在做 Agent 项目,**强烈建议直接用 LangGraph 而不是 AgentExecutor**——别走弯路了。

> **LangGraph 不是 LangChain 的"替代",是 LangChain 的"进化"——理解这点,Agent 工程化就入门了**。
