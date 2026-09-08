---
title: Multi-Agent 协作——CrewAI、MetaGPT、AutoGen 三种框架实测
categories:
  - AI
tags:
  - Agent
  - Multi-Agent
  - CrewAI
  - MetaGPT
  - AutoGen
description: 多 Agent 协作是 2024-2026 年最热的方向。CrewAI、MetaGPT、AutoGen 三个框架差别巨大,选错了浪费 3 个月。
date: 2026-07-31 10:00:00
---

# Multi-Agent 协作——CrewAI、MetaGPT、AutoGen 三种框架实测

> 多 Agent 协作是 Agent 领域最热的方向。**但 CrewAI、MetaGPT、AutoGen 三个框架差别巨大——选错了浪费 3 个月**。

## 什么是 Multi-Agent

**Multi-Agent = 多个 Agent 协作完成复杂任务**。

类比公司:
- 单 Agent = 一个员工独立干活
- Multi-Agent = 一个团队分工合作

**核心思想**:
- 每个 Agent 有明确角色(产品经理 / 工程师 / 测试)
- Agent 之间通过消息传递协作
- 通过工作流编排完成复杂任务

## 三个框架的定位

### CrewAI:角色扮演 + 流程编排

**核心思想**:像管一个团队一样管理 Agent。

```python
from crewai import Agent, Task, Crew

# 定义 Agent
researcher = Agent(
    role="研究员",
    goal="研究某个主题并产出报告",
    backstory="你是一个资深研究员,擅长深度调研"
)

writer = Agent(
    role="作家",
    goal="把研究报告写成易读的博客",
    backstory="你是一个技术作家,擅长把复杂概念讲清楚"
)

# 定义任务
research_task = Task(
    description="研究 AI Agent 的最新进展",
    agent=researcher,
    expected_output="详细研究报告"
)

write_task = Task(
    description="基于报告写一篇 1500 字博客",
    agent=writer,
    expected_output="可直接发布的博客文章"
)

# 组装团队
crew = Crew(
    agents=[researcher, writer],
    tasks=[research_task, write_task],
    verbose=True
)

result = crew.kickoff()
```

**优点**:
- 上手快,5 分钟能跑通
- 角色化思维,贴近业务
- 任务依赖管理直观

**缺点**:
- 适合"流程化"任务,**不适合复杂规划**
- 调试困难,出错信息不清晰
- 中文支持一般

### MetaGPT:模拟公司流程

**核心思想**:把整个"软件公司"流程化——产品经理 → 架构师 → 工程师 → 测试。

```python
from metagpt.software_company import SoftwareCompany

# 启动"软件公司"
company = SoftwareCompany()
company.hire([
    ProductManager(),
    Architect(),
    ProjectManager(),
    Engineer(),
    QaEngineer()
])

# 给需求,自动产出代码 + 文档 + 测试
company.run("开发一个待办事项应用")
```

**MetaGPT 会产出**:
- 需求文档(由 PM Agent 写)
- 设计文档(由 Architect Agent 写)
- 代码(由 Engineer Agent 写)
- 测试用例(由 QA Agent 写)

**优点**:
- 完整模拟"软件工程流程"
- 文档齐全,适合学习软件工程
- 一次产出多份资产

**缺点**:
- **重**,启动一个项目要 5-10 分钟
- **复杂任务质量一般**——简单 demo 不错,生产项目不行
- **不够灵活**——流程是预设的,改起来麻烦

### AutoGen:微软出品,对话驱动

**核心思想**:用"群聊"的方式组织 Agent 协作。

```python
from autogen import AssistantAgent, UserProxyAgent, GroupChat

# 定义 Agent
assistant = AssistantAgent(
    name="assistant",
    llm_config={"model": "gpt-4o"}
)

user_proxy = UserProxyAgent(
    name="user_proxy",
    code_execution_config={"work_dir": "coding"}
)

# 让两个 Agent 协作
user_proxy.initiate_chat(
    assistant,
    message="写一个 Python 函数计算斐波那契数列"
)
```

**核心特性**:
- 支持 `GroupChat`:多个 Agent 群聊
- 支持 `嵌套对话`:Agent 之间可以开小会
- 支持 `人工介入`:用户可以中途插入

**优点**:
- 微软背书,生态好
- 灵活度高,适合研究
- 支持复杂对话模式

**缺点**:
- 学习曲线陡
- 文档质量一般
- 性能调优困难

## 三种框架的实测对比

我做了个测试——**让三个框架完成同一组任务**:

任务集:
1. 调研"LLM 推理优化"主题,产出 2000 字报告
2. 设计一个 Todo App,产出代码 + 文档
3. 模拟一场 5 人会议,讨论"是否上 AI Agent"
4. 翻译并润色一篇英文论文

### 评测维度

- **完成度**:任务是否真的做完
- **质量**:产出物的可用性
- **速度**:耗时
- **Token 消耗**:成本
- **可调试性**:出错能否定位

### 结果

| 框架 | 完成度 | 质量 | 速度 | Token | 调试 |
|---|---|---|---|---|---|
| CrewAI | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 中 | 中 |
| MetaGPT | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | 高 | 难 |
| AutoGen | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | 中高 | 中 |

### 具体观察

**调研任务**:
- CrewAI:角色清晰,流程顺,产出可用
- MetaGPT:太重,产出一堆不必要文档
- AutoGen:灵活但容易跑偏

**代码任务**:
- CrewAI:只能产简单代码
- MetaGPT:完整工程但代码质量一般
- AutoGen:灵活,可调深度

## 我的实际项目经验

### 项目 1:研究助手(用 CrewAI)

```python
# CrewAI 实现
researcher = Agent(role="研究员", goal="深度调研", backstory="...")
critic = Agent(role="评论家", goal="挑刺", backstory="...")
writer = Agent(role="作家", goal="写作", backstory="...")

tasks = [
    Task("调研", agent=researcher),
    Task("评论", agent=critic),  # 给研究员反馈
    Task("修改", agent=researcher),
    Task("写作", agent=writer)
]
```

**效果**:研究质量提升 30%,**多了一个"评论"环节是关键**。

### 项目 2:代码生成(用 LangGraph + 单 Agent)

**没选 MetaGPT**——MetaGPT 太重,我的需求是"单文件代码生成",不需要完整工程流程。

**也没选 AutoGen**——AutoGen 灵活但难以调试。

**单 Agent + LangGraph + Reflection** 反而最实用。

### 项目 3:复杂规划(用 AutoGen)

需要 5 个 Agent 讨论一个商业方案——**AutoGen 的 GroupChat 最合适**。

CrewAI 也能做,但角色固定,讨论不自然。
MetaGPT 没有"讨论"模式。

## Multi-Agent 的真实价值

### 价值 1:角色分工

不同 Agent 擅长不同事:
- **研究型 Agent**:擅长查资料
- **写作型 Agent**:擅长文字
- **代码型 Agent**:擅长代码
- **评论型 Agent**:擅长挑刺

**混用比单 Agent 强**。

### 价值 2:流程编排

Multi-Agent 框架**强制你思考"工作流"**——
- 谁先做?
- 谁检查?
- 谁修改?
- 谁发布?

这种"显式流程"**让复杂任务可控**。

### 价值 3:多视角

让多个 Agent 对同一问题发表意见——**投票/辩论**,结果更鲁棒。

### 价值 4:可解释性

Multi-Agent 系统的"消息流"**就是天然的日志**——用户能看到每个 Agent 怎么想、怎么做。

## Multi-Agent 的几个坑

### 坑 1:Agent 太多,沟通成本爆炸

10 个 Agent 协作——**消息传递指数增长**,成本爆炸。

**经验**:3-5 个 Agent 是上限。

### 坑 2:循环依赖

Agent A 等 Agent B 的结果,Agent B 等 Agent A 的反馈——**死锁**。

```python
# 必须避免循环
graph = StateGraph()
graph.add_edge(A, B)
graph.add_edge(B, C)
# 不要:graph.add_edge(C, A)
```

### 坑 3:沟通协议不清晰

Agent A 给 Agent B 发了一段乱糟糟的消息——**B 理解偏了**。

**必须**:
- 用结构化消息(JSON schema)
- 每条消息明确"主题 + 内容 + 期望回复"

### 坑 4:成本失控

每个 Agent 都调 GPT-4o,一次任务调 20 次——**$2/任务**。

生产场景:**降级用小模型**——简单 Agent 用 GPT-4o-mini,只有"主决策"用 GPT-4o。

## 写在最后

Multi-Agent 是 Agent 工程的"必经之路"——但**没有"最好框架",只有"最适合场景"**。

我的选择建议:

| 场景 | 推荐框架 |
|---|---|
| 简单研究/写作 | **CrewAI**(上手快) |
| 完整软件工程 demo | **MetaGPT**(流程完整) |
| 复杂规划/讨论 | **AutoGen**(灵活) |
| 生产 Agent 系统 | **LangGraph**(可控) |
| 简单代码生成 | **单 Agent + Reflection**(够用) |

**别为了"用 Multi-Agent"而用——单 Agent 能解决的,别上 Multi-Agent**。

> **Multi-Agent 的真正价值,不是"让 AI 更聪明"——是"让复杂任务更可控、更可解释、更可调试"**。
