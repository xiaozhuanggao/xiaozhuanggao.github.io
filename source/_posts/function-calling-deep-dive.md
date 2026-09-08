---
title: Function Calling / Tool Use 协议详解——从 JSON Schema 到多轮调用
categories:
  - AI
tags:
  - 大模型
  - Function Calling
  - Tool Use
  - Agent
description: 模型怎么决定"调哪个工具、传什么参数"?看懂了 Function Calling，就看懂了一半 Agent。
date: 2026-07-09 10:00:00
---

# Function Calling / Tool Use 协议详解——从 JSON Schema 到多轮调用

> Agent 的核心是"调工具"。但模型是怎么决定"调哪个工具、传什么参数"的?**这一节彻底讲清楚**。

## 什么是 Function Calling

Function Calling(也叫 Tool Use)是 LLM 的一个能力——**模型根据用户意图,自动选择并调用外部工具**。

最简单的例子:
- 用户问"今天上海天气怎么样?"
- 模型不直接回答,而是**返回一个 JSON**:
  ```json
  {
    "tool": "get_weather",
    "params": {"city": "上海"}
  }
  ```
- 你的代码拿到这个 JSON,**真的去调用天气 API**
- 把结果再喂给模型
- 模型**根据工具结果生成最终回答**

这是 Agent 的基石。

## Function Calling 的协议格式

各家协议大同小异,以 OpenAI 为例:

### 1. 定义工具(JSON Schema)

```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "查询指定城市的天气",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "城市名称,如'上海'"
                    }
                },
                "required": ["city"]
            }
        }
    }
]
```

**几个关键字段**:

- **name**:工具名,**必须是英文 + 下划线**,不能有空格
- **description**:工具描述——**模型就是看这个决定调不调**
- **parameters**:参数 schema,标准 JSON Schema

### 2. 模型返回 tool_calls

```json
{
  "tool_calls": [
    {
      "id": "call_abc123",
      "type": "function",
      "function": {
        "name": "get_weather",
        "arguments": "{\"city\": \"上海\"}"
      }
    }
  ]
}
```

注意 `arguments` 是**字符串,不是对象**——需要 `json.loads()`。

### 3. 把工具结果喂回去

```python
messages.append({
    "role": "tool",
    "tool_call_id": "call_abc123",
    "content": "{\"temperature\": 28, \"weather\": \"晴\"}"
})
```

**role 必须是 "tool"**——告诉模型这是工具结果。

## Function Calling 的几个坑

### 坑 1:description 写得太简单

很多新手写:
```
"name": "search",
"description": "搜索"
```

模型看了:**不知道该调还是不该调、该传什么参数**。

正确写法:
```
"name": "search_internal_docs",
"description": "在内部知识库中搜索文档,用于回答用户关于公司政策、产品手册、技术规范的提问。每次调用必须传入 query 参数。"
```

**description 是模型"理解工具的唯一线索"**——必须写得**像教一个新人**。

### 坑 2:参数嵌套过深

```json
{
  "parameters": {
    "type": "object",
    "properties": {
      "filters": {
        "type": "object",
        "properties": {
          "date_range": {
            "type": "object",
            "properties": {
              "start": {"type": "string"},
              "end": {"type": "string"}
            }
          }
        }
      }
    }
  }
}
```

模型经常**填错或漏填**嵌套字段。

**优化**:扁平化参数,顶层不超过 3 层。

### 坑 3:返回结果太长

工具返回 10000 字给模型——**模型会"迷失"在信息里**。

**优化**:
- 工具返回前**先做摘要**(1000 字以内)
- 或者让模型自己选择"要不要全量"
- 用 RAG 思路:**只返回最相关的 Top-K**

### 坑 4:并行调用

模型一次返回多个 tool_calls 时——**应该并行执行,不要串行**。

```python
# 错:串行
for call in response.tool_calls:
    result = execute(call)
    messages.append(...)

# 对:并行
results = await asyncio.gather(*[execute(c) for c in response.tool_calls])
```

**并行调用能省 60%+ 延迟**。

## Function Calling vs Tool Use

不同厂商叫法不同:

| 厂商 | 叫法 |
|---|---|
| OpenAI | Function Calling / Tools |
| Anthropic | Tool Use |
| Google | Function Calling |
| Meta | Tool Use |
| Mistral | Function Calling |

**协议本质相同**——但具体格式有差异。

实际开发时,**用框架(LangChain/LlamaIndex)能屏蔽差异**。

## 进阶:多轮 Function Calling

真实 Agent 经常**多轮调用**:

```
用户:帮我订后天上海到北京的机票,要下午的,经济舱

轮1: get_flights(departure_date, from, to)
轮2: filter_flights(departure_date, time_range, class)
轮3: book_flight(flight_id, passenger_info)
```

每轮的 tool_calls 都依赖上一轮的结果。

**实现关键**:
- 维护一个完整的 messages 列表(包括 tool_calls 和 tool 结果)
- 用 while 循环,直到模型不再返回 tool_calls
- 设置**最大循环次数**(防止死循环)

```python
MAX_ITERATIONS = 10
for i in range(MAX_ITERATIONS):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        tools=tools
    )
    if not response.choices[0].message.tool_calls:
        break
    # 执行工具
    for call in response.choices[0].message.tool_calls:
        result = execute_tool(call)
        messages.append({
            "role": "tool",
            "tool_call_id": call.id,
            "content": result
        })
```

## Function Calling 的失败模式

我统计过自己项目里的 Function Calling 失败情况:

| 失败类型 | 占比 |
|---|---|
| 参数缺失/类型错 | 35% |
| 调错工具 | 25% |
| 工具返回解析失败 | 20% |
| 死循环(反复调同一工具) | 15% |
| 其他 | 5% |

**最大头是"参数错误"**——靠 Prompt 优化和工具描述优化能改善,但**做不到 100% 准确**。

Agent 系统设计时,**必须做"工具调用失败"的兜底**——比如重试、降级、人工接管。

## 写在最后

Function Calling 是 Agent 时代的基石协议——**看不懂这个,就看不懂 Agent**。

但它有个**根本限制**:模型只能"选择 + 传参",不能"规划复杂流程"。

这就要靠 **Agent 架构(ReAct / Plan-and-Execute)** 来补——下一篇文章讲。

> **Function Calling 是"工具",Agent 是"用法"。两者结合,才是真正的智能体**。
