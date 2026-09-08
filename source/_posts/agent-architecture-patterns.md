---
title: Agent 架构模式——ReAct、Plan-and-Execute、Reflection 三大范式实战对比
categories:
  - AI
tags:
  - Agent
  - 架构
  - ReAct
  - Plan-and-Execute
  - Reflection
description: 同样是 Agent，ReAct、Plan-and-Execute、Reflection 三种架构差别巨大。选错了浪费 3 倍成本。
date: 2026-07-22 10:00:00
---

# Agent 架构模式——ReAct、Plan-and-Execute、Reflection 三大范式实战对比

> 同样是 Agent，"边想边做"、"先想再做"、"做后再想"——三种架构差别巨大。**选错了成本能差 3 倍**。

## 三种架构的核心区别

### ReAct(边想边做)

```
思考 1 → 行动 1 → 观察 1 → 思考 2 → 行动 2 → ... → 结束
```

**特点**:每一步都基于上一步的结果,**强适应性**。

### Plan-and-Execute(先想再做)

```
计划 → 行动 1 → 行动 2 → ... → 行动 N → 总结
```

**特点**:先一次性规划好所有步骤,**强一致性**。

### Reflection(做后再想)

```
行动 → 反思 → 改进行动 → 反思 → ... → 结束
```

**特点**:每次行动后都"复盘",**强改进能力**。

## ReAct 深度解析

### 工作流程

```python
class ReActAgent:
    def __init__(self, llm, tools, max_iter=10):
        self.llm = llm
        self.tools = tools
        self.max_iter = max_iter
    
    def run(self, question):
        history = ""
        for i in range(self.max_iter):
            prompt = REACT_TEMPLATE.format(
                question=question,
                history=history,
                tools=self.tool_descriptions()
            )
            response = self.llm(prompt)
            thought, action = self._parse(response)
            
            if action.name == "Finish":
                return action.answer
            
            result = self.tools.execute(action)
            history += f"\n思考:{thought}\n行动:{action}\n观察:{result}\n"
```

### 优点

- **自适应强**:每步根据结果调整
- **实现简单**:循环 + Prompt 即可
- **LangChain 原生支持**:AgentExecutor 默认就是 ReAct

### 缺点

- **容易走偏**:模型可能陷入"反复调同一工具"的死循环
- **Token 消耗大**:每步都要重新生成思考
- **缺乏全局规划**:只看眼前,不看长远

## Plan-and-Execute 深度解析

### 工作流程

```python
class PlanExecuteAgent:
    def __init__(self, planner_llm, executor_llm, tools):
        self.planner = planner_llm      # 通常用 GPT-4o
        self.executor = executor_llm    # 可以用小模型
        self.tools = tools
    
    def run(self, question):
        # Step 1: 制定计划
        plan = self.planner(PLAN_TEMPLATE.format(question=question))
        steps = self._parse_plan(plan)  # ["step1", "step2", "step3"]
        
        # Step 2: 执行每步
        results = []
        for step in steps:
            result = self.executor(STEP_TEMPLATE.format(
                step=step,
                context=results
            ))
            results.append(result)
        
        # Step 3: 总结
        return self.planner(SUMMARY_TEMPLATE.format(
            question=question,
            plan=plan,
            results=results
        ))
```

### 优点

- **Token 效率高**:计划一次生成,不每步重算
- **可解释性强**:用户能看到完整计划
- **可以用小模型执行**:只要 plan 准,执行可以便宜

### 缺点

- **计划可能错**:如果第一步规划错了,后面全错
- **不适应变化**:中途环境变了,计划不调整
- **实现复杂**:需要单独的 planner + executor

## Reflection 深度解析

### 工作流程

```python
class ReflectionAgent:
    def __init__(self, actor_llm, reflector_llm, tools):
        self.actor = actor_llm
        self.reflector = reflector_llm
        self.tools = tools
    
    def run(self, question, max_attempts=3):
        for attempt in range(max_attempts):
            # Step 1: 执行
            result = self.actor(ACTOR_TEMPLATE.format(
                question=question,
                previous_attempts=self.history
            ))
            
            # Step 2: 反思
            reflection = self.reflector(REFLECTOR_TEMPLATE.format(
                question=question,
                result=result
            ))
            
            # Step 3: 判断
            if "PASS" in reflection:
                return result
            
            self.history.append({
                "result": result,
                "reflection": reflection
            })
        
        return self.history[-1]["result"]
```

### 优点

- **自我改进**:失败会"反思原因",下次做得更好
- **适合代码/SQL 生成**:有明确对错,反思有效

### 缺点

- **成本极高**:每次失败重做 + 反思,**3 倍 Token**
- **依赖评估能力**:模型要能"判断对错"
- **不适用主观任务**:写诗、写文章没法"反思"

## 三种架构的实测对比

我做了个测试——**让三个 Agent 完成同一组任务**:

任务集:
1. 查询"上海到北京明天的高铁"
2. 分析一份财报并写摘要
3. 写一个 Python 排序函数
4. 规划一次 3 天旅游行程
5. 多步调试一个 bug

| 任务 | ReAct | Plan-Execute | Reflection |
|---|---|---|---|
| 1. 简单查询 | ⭐⭐⭐⭐⭐ 快准 | ⭐⭐⭐ 慢一点 | ⭐⭐ 太重 |
| 2. 财报分析 | ⭐⭐⭐ 走偏 | ⭐⭐⭐⭐⭐ 清晰 | ⭐⭐⭐⭐ 不断改 |
| 3. 排序函数 | ⭐⭐ 反复试 | ⭐⭐⭐ 一般 | ⭐⭐⭐⭐⭐ 改到对 |
| 4. 旅游行程 | ⭐⭐⭐⭐ 不错 | ⭐⭐⭐⭐⭐ 完整 | ⭐⭐ 反复改 |
| 5. 多步调试 | ⭐⭐⭐⭐ 自适应 | ⭐⭐ 卡住 | ⭐⭐⭐⭐⭐ 越改越好 |

### 结论

**没有"最好",只有"最适合"**:

- 简单任务 → **ReAct**
- 需要规划感 → **Plan-and-Execute**
- 代码生成/调试 → **Reflection**
- 长流程多步 → **Plan-and-Execute**

## 混合架构:生产系统的选择

实际项目里,**很少用纯一种架构**。更常见的是混合:

### 模式 1:Plan-and-Execute + Reflection

```
Planner 制定计划
  ↓
Executor 执行 Step 1 → Reflector 检查 → 通过/改进
  ↓
Executor 执行 Step 2 → Reflector 检查 → 通过/改进
  ↓
...
  ↓
汇总
```

### 模式 2:ReAct + Plan-and-Execute

```
Planner 制定大框架
  ↓
对每个 Step,用 ReAct 自主探索
  ↓
汇总
```

### 模式 3:Plan-Execute + 动态重规划

```
Planner 制定初始计划
  ↓
执行 Step N
  ↓
如果遇到错误 → Re-Planner 重新规划
  ↓
继续
```

**真实系统的 Agent 架构,通常是这样"嵌套+循环"的复杂结构**。

## 我的项目实战经验

### 项目 1:客服 Agent

**用 ReAct**——简单多步对话,ReAct 最合适。

效果:80% 任务 3 步内解决,平均 1500 Token/对话。

### 项目 2:研究助手

**用 Plan-and-Execute**——需要"先列大纲,再填充"。

效果:用户能看到完整研究计划,可解释性强。

### 项目 3:代码生成 Agent

**用 Reflection**——代码有"对错",反思有效。

效果:首轮成功率 65%,反思后达 88%。

## 写在最后

Agent 架构没有"银弹"——**不同任务需要不同架构**。

选架构的核心原则:
1. **看任务类型**:简单多步 vs 复杂规划 vs 反复改进
2. **看成本预算**:Reflection 是 3 倍 Token,生产要算账
3. **看可解释性**:用户能看到 Agent 的"思考过程"很重要
4. **看维护成本**:架构越复杂,后期维护越难

> **最好的 Agent 架构,是"用最简单的架构解决 80% 的问题,剩下 20% 才用复杂架构"**。
