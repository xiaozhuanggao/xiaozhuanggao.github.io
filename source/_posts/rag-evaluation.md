---
title: RAG 评估体系——怎么知道你的 RAG 系统好不好
categories:
  - AI
tags:
  - RAG
  - 评估
  - 指标
  - 工程化
description: 没有评估指标,RAG 优化就是盲改。这套评估体系帮我把准确率从 70% 推到 92%。
date: 2026-08-29 10:00:00
---

# RAG 评估体系——怎么知道你的 RAG 系统好不好

> 没有评估指标,RAG 优化就是盲改。**这套评估体系帮我把准确率从 70% 推到 92%**。

## 为什么 RAG 评估难

### 传统软件评估简单

输入 → 输出 → 对比预期,准确率一目了然。

### RAG 评估复杂

**RAG 系统的输出受多因素影响**:
- 检索质量(召回了什么文档)
- LLM 能力(怎么生成答案)
- Prompt 设计(怎么拼上下文)
- 文档质量(原始数据好不好)

**评估不能只看"最终答案对不对"**——还要看"中间环节哪里出问题"。

## RAG 评估的三个层面

### 层面 1:检索质量

**判断检索召回的文档是否相关**。

指标:
- **Recall@K**:Top-K 召回了多少相关文档
- **Precision@K**:Top-K 召回了多少"假相关"文档
- **MRR**(Mean Reciprocal Rank):第一个相关文档的排名倒数

### 层面 2:答案质量

**判断最终生成的答案是否正确**。

指标:
- **Answer Relevance**:答案是否切题
- **Faithfulness**:答案是否忠于检索内容(不胡编)
- **Correctness**:答案是否事实正确

### 层面 3:用户体验

**判断真实用户使用感受**。

指标:
- **满意度**(用户反馈)
- **响应时间**(延迟)
- **采用率**(用户是否真的用)

## 评估数据集准备

### 1. 准备测试集

**最重要的步骤**——没有测试集,所有评估都是"感觉"。

```python
test_questions = [
    {
        "question": "公司的年假政策是什么?",
        "expected_answer": "员工每年享有 7 天年假...",
        "expected_doc_ids": ["policy_001", "policy_002"],  # 相关文档
        "difficulty": "easy"
    },
    {
        "question": "如何在系统中重置密码?",
        "expected_answer": "登录页面点击'忘记密码'...",
        "expected_doc_ids": ["faq_005"],
        "difficulty": "medium"
    },
    # ... 至少 100 条
]
```

**测试集要包含**:
- 简单问题(直接答案)
- 中等问题(需要推理)
- 难题(检索不到)
- 刁钻问题(超出知识库范围)

### 2. 测试集来源

| 来源 | 优点 | 缺点 |
|---|---|---|
| 真实用户问题 | 真实场景 | 需要积累 |
| 人工标注 | 质量高 | 费时费力 |
| LLM 生成 | 快 | 质量参差 |
| 公开数据集 | 标准 | 不一定适合 |

**建议**:真实问题为主 + LLM 补充 + 人工 review。

## 评估指标详解

### 1. 检索质量指标

```python
def recall_at_k(retrieved_ids, expected_ids, k=10):
    """Top-K 召回率"""
    retrieved_top_k = set(retrieved_ids[:k])
    expected = set(expected_ids)
    if not expected:
        return 0
    return len(retrieved_top_k & expected) / len(expected)

def precision_at_k(retrieved_ids, expected_ids, k=10):
    """Top-K 准确率"""
    retrieved_top_k = set(retrieved_ids[:k])
    if not retrieved_top_k:
        return 0
    expected = set(expected_ids)
    return len(retrieved_top_k & expected) / len(retrieved_top_k)

def mrr(retrieved_ids, expected_ids):
    """第一个相关文档的排名倒数"""
    for i, doc_id in enumerate(retrieved_ids):
        if doc_id in expected_ids:
            return 1 / (i + 1)
    return 0
```

### 2. 答案质量指标(用 LLM 评估)

```python
EVAL_PROMPT = """
你是评估员,判断 AI 回答的质量。

问题: {question}
AI 回答: {answer}
标准答案: {expected}

从三个维度评分(1-5):

1. Answer Relevance(答案相关性):
   1: 完全答非所问
   5: 完美回答问题

2. Faithfulness(忠实度):
   1: AI 编造了内容
   5: 完全基于检索内容

3. Correctness(正确性):
   1: 答案错误
   5: 与标准答案一致

输出 JSON:{{"relevance": 5, "faithfulness": 4, "correctness": 5, "reason": "..."}}
"""

def evaluate_with_llm(question, answer, expected, llm):
    prompt = EVAL_PROMPT.format(
        question=question,
        answer=answer,
        expected=expected
    )
    response = llm(prompt)
    return json.loads(response)
```

### 3. 综合评分

```python
def rag_evaluate(test_set, rag_system, llm):
    results = []
    for item in test_set:
        # 跑 RAG
        retrieved = rag_system.retrieve(item["question"])
        answer = rag_system.generate(item["question"], retrieved)
        
        # 检索质量
        recall = recall_at_k(retrieved, item["expected_doc_ids"])
        
        # 答案质量
        scores = evaluate_with_llm(item["question"], answer, item["expected_answer"], llm)
        
        results.append({
            "recall": recall,
            "relevance": scores["relevance"],
            "faithfulness": scores["faithfulness"],
            "correctness": scores["correctness"]
        })
    
    # 汇总
    avg = {
        "recall": mean([r["recall"] for r in results]),
        "relevance": mean([r["relevance"] for r in results]),
        "faithfulness": mean([r["faithfulness"] for r in results]),
        "correctness": mean([r["correctness"] for r in results])
    }
    
    return avg
```

## RAGAS 框架(推荐)

**RAGAS** 是专门评估 RAG 系统的开源框架——**免去自己写评估代码**。

### 安装

```bash
pip install ragas
```

### 使用

```python
from ragas import evaluate
from ragas.metrics import (
    context_relevancy,
    faithfulness,
    answer_relevancy,
    answer_correctness
)

# 准备数据
data = {
    "question": [...],
    "contexts": [...],  # 检索到的文档
    "answer": [...],    # RAG 生成的答案
    "ground_truth": [...]  # 标准答案
}

# 评估
result = evaluate(data, metrics=[
    context_relevancy,    # 检索质量
    faithfulness,         # 忠实度
    answer_relevancy,     # 答案相关性
    answer_correctness    # 正确性
])

print(result)
```

**输出**:
```
context_relevancy: 0.85
faithfulness: 0.92
answer_relevancy: 0.88
answer_correctness: 0.79
```

**一目了然**——哪个环节出问题、问题多大。

## 我的 RAG 评估体系

我用了 6 个月时间搭建的体系——

### 工具栈

| 工具 | 用途 |
|---|---|
| RAGAS | 自动评估指标 |
| LangSmith | 调用追踪 |
| Phoenix(arize) | 调试可视化 |
| 自建 dashboard | 趋势监控 |

### 评估流程

**日常**(每次发版):
```bash
# 1. 跑 200 条测试集
python eval/run_eval.py --test tests/v2.json

# 2. 对比上次结果
python eval/compare.py current.json baseline.json

# 3. 失败案例分析
python eval/failure_analysis.py
```

**每周**:
- 分析失败 case
- 更新测试集
- 优化重点场景

### 评估看板

我搭了一个 Grafana 看板,监控:

- 整体 Recall / Precision
- 按类别拆分(技术问题 / 账单问题 / ...)
- 按难度拆分(简单 / 中等 / 难)
- LLM 调用 Token 成本
- 响应延迟 P50 / P99

**任何一项恶化,立即报警**。

## 几个核心经验

### 1. 测试集要"够刁"

**简单问题谁都能做对**——测试集要包含**真正难的问题**:
- 多跳推理("X 和 Y 的关系是什么?")
- 跨文档("对比 A 和 B 的差异")
- 边界情况("文档里没说怎么办")

### 2. 评估指标要分层

**不要只看一个数字**——

```
总平均: 0.85 ← 这个数字没用
├── 检索质量: 0.92 ← OK
├── 答案质量: 0.78 ← 这里有问题!
│   ├── 简单问题: 0.95
│   ├── 中等问题: 0.80
│   └── 难题: 0.45 ← 难题特别差
```

**分层才能定位问题**。

### 3. 失败案例比成功案例重要

**10 个失败案例 > 100 个成功案例**——失败案例告诉你**哪里要改**。

```python
# 保存所有失败案例
for result in eval_results:
    if result["correctness"] < 3:
        save_to_failure_db(result)
```

每周 review 失败 case,**找到共性,批量优化**。

### 4. 防止"过拟合到测试集"

**测试集也不能一成不变**——

- 季度更新一次(加新问题)
- 加"对抗样本"(故意刁难)
- 留 20% 测试集**永远不参与训练/优化**

### 5. 用户反馈是黄金数据

**真实用户反馈 > 任何评估指标**——

```python
# 收集用户反馈
for conversation in user_conversations:
    if conversation.user_feedback:
        # 加入训练集
        add_to_test_set(conversation)
```

**3 个月后,测试集会非常接近真实场景**。

## 实战优化案例

我用评估体系,把一个 RAG 系统从 70% 推到 92%:

### 阶段 1:Baseline 评估

```
Recall@10: 0.65
Faithfulness: 0.85
Correctness: 0.70
```

### 阶段 2:定位问题

分析失败 case 发现:
- 检索召回率低(Recall 0.65)
- 答案冗长、爱"扩展"(Faithfulness 高但 Correctness 低)

### 阶段 3:针对性优化

| 优化 | 提升 |
|---|---|
| Embedding 模型升级(BGE-large) | Recall +15% |
| Hybrid 检索(BM25 + 向量) | Recall +8% |
| Query 改写 | Recall +5% |
| 限制 LLM 输出长度 | Correctness +7% |
| 强化 Prompt(要求简洁) | Correctness +5% |

### 阶段 4:重新评估

```
Recall@10: 0.93
Faithfulness: 0.91
Correctness: 0.92
```

**准确率从 70% → 92%**——**所有优化都基于评估数据**。

## 写在最后

RAG 评估不是"做一次就完"——**是持续迭代**。

我的建议:
1. **第一周**:搭评估体系(RAGAS + 自建)
2. **第二周**:准备测试集(200+ 条)
3. **第三周**:跑 baseline
4. **之后**:每次优化前先评估,优化后再评估

**没有评估的 RAG 优化,都是在"赌"**。

> **RAG 工程的本质,是"用数据驱动优化"——评估体系就是数据来源**。
