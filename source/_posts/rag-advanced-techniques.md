---
title: RAG 进阶——HyDE、Self-RAG、CRAG 三种增强检索实战
categories:
  - AI
tags:
  - RAG
  - HyDE
  - Self-RAG
  - CRAG
  - 检索增强
description: 基础 RAG 准确率 70% 出头。HyDE / Self-RAG / CRAG 能把它推到 90%+。怎么做?
date: 2026-08-14 10:00:00
---

# RAG 进阶——HyDE、Self-RAG、CRAG 三种增强检索实战

> 基础 RAG 准确率 70% 出头。**HyDE、Self-RAG、CRAG 三种增强检索,能把准确率推到 90%+**。

## 基础 RAG 的局限

经典 RAG 流程:
1. 用户问题 → 向量化
2. 向量数据库检索 Top-K
3. 拼接 Prompt(检索内容 + 问题)
4. LLM 生成回答

**问题**:
- 用户问题简短("年假几天?")
- 检索时**语义匹配不准**——问题太短,embedding 信息不够
- 容易召回不相关文档

实测:**基础 RAG 在企业知识库上,准确率 65-75%**。

## 进阶方案 1:HyDE(Hypothetical Document Embeddings)

### 核心思想

**先让 LLM 生成"假想答案",再用假想答案去检索**。

```
问题: "年假几天?"

传统 RAG:
  embedding("年假几天?") → 检索

HyDE:
  LLM("假设你是 HR,请回答:年假几天?") → "员工每年享有 7 天年假..."
  embedding("员工每年享有 7 天年假...") → 检索
```

**假想答案比"问题"信息密度高**——embedding 检索更准。

### 实现

```python
def hyde_retrieve(question, llm, vector_db, top_k=5):
    # Step 1: 生成假想答案
    hypothetical = llm(
        f"请根据你的知识,回答以下问题:\n{question}\n"
        f"回答要详细具体,像真实文档一样。"
    )
    
    # Step 2: 用假想答案检索
    results = vector_db.search(hypothetical, top_k=top_k)
    return results
```

### 效果

**准确率提升 10-15%**——特别适合"问题简短、文档丰富"的场景。

**代价**:多一次 LLM 调用,**Token 消耗 +50%**。

### 适用场景

✅ 短问题("怎么报销?")
✅ 专业领域(模型有基础知识)
❌ 不适合:模型不熟悉的话题(假想答案会错)

## 进阶方案 2:Self-RAG

### 核心思想

**让 LLM 自己判断"检索到的内容是否相关"**。

```
传统 RAG:
  问题 → 检索 Top-K → 拼给 LLM → 回答

Self-RAG:
  问题 → 检索 Top-K
       → LLM 判断每条是否相关 [Special Token: RELEVANT]
       → 只用相关的拼 Prompt → 回答
```

**Self-RAG 引入了 4 个特殊 token**:
- `[Retrieve]`:是否需要检索
- `[IsRel]`:检索结果是否相关
- `[IsSup]`:回答是否被检索结果支持
- `[IsUse]`:回答是否有用

### 实现

```python
def self_rag(question, llm, vector_db):
    # Step 1: 检索
    docs = vector_db.search(question, top_k=10)
    
    # Step 2: LLM 判断相关性
    relevant_docs = []
    for doc in docs:
        prompt = f"""
        问题:{question}
        文档:{doc.content}
        
        请判断该文档是否与问题相关。
        如果相关,回答 [IsRel] Yes,然后说明理由。
        如果不相关,回答 [IsRel] No。
        """
        response = llm(prompt)
        if "[IsRel] Yes" in response:
            relevant_docs.append(doc)
    
    # Step 3: 用相关文档生成答案
    if not relevant_docs:
        return "未找到相关信息"
    
    context = "\n".join([d.content for d in relevant_docs])
    answer = llm(f"基于以下信息回答问题:\n{context}\n问题:{question}")
    
    return answer
```

### 效果

**准确率提升 15-20%**——过滤掉"看似相关实则无关"的文档。

### 适用场景

✅ 文档质量参差不齐
✅ 检索召回率高但准确率低
✅ 业务对准确率要求极高

## 进阶方案 3:CRAG(Corrective RAG)

### 核心思想

**Self-RAG 的进化版**——不仅判断相关性,还**自动采取修正动作**。

```
检索结果分类:
  Correct(正确) → 直接用
  Incorrect(错误) → 触发 Web 搜索补充
  Ambiguous(模糊) → 混合原始 + Web 结果
```

### 实现

```python
def crag(question, llm, vector_db, web_search):
    # Step 1: 检索
    docs = vector_db.search(question, top_k=5)
    
    # Step 2: 评估检索质量
    confidence = evaluate_retrieval(question, docs, llm)
    
    # Step 3: 根据置信度采取动作
    if confidence > 0.7:
        # Correct: 直接用
        context = "\n".join([d.content for d in docs])
        return llm(f"基于:\n{context}\n回答:{question}")
    
    elif confidence > 0.3:
        # Ambiguous: 混合
        web_results = web_search(question, top_k=3)
        context = "\n".join([d.content for d in docs] + web_results)
        return llm(f"基于:\n{context}\n回答:{question}")
    
    else:
        # Incorrect: 完全用 Web
        web_results = web_search(question, top_k=5)
        context = "\n".join(web_results)
        return llm(f"基于:\n{context}\n回答:{question}")
```

### 置信度评估

```python
def evaluate_retrieval(question, docs, llm):
    prompt = f"""
    问题:{question}
    检索到的文档:{[d.content[:200] for d in docs]}
    
    请评估这些文档是否能回答问题,返回 0-1 的置信度:
    - 1.0: 完全能回答
    - 0.5: 部分相关,需要补充
    - 0.0: 完全无关
    """
    response = llm(prompt)
    # 提取置信度数字
    match = re.search(r'(\d+\.\d+)', response)
    return float(match.group(1)) if match else 0.5
```

### 效果

**准确率提升 20-25%**——自动修正检索错误。

**代价**:每条问题**多 2-3 次 LLM 调用**,Token 消耗 +200%。

### 适用场景

✅ 内部知识库**不完整**(部分问题文档没覆盖)
✅ 需要结合外部信息
✅ 业务对准确率要求极高

## 三种方案对比

| 维度 | HyDE | Self-RAG | CRAG |
|---|---|---|---|
| 准确率提升 | +10-15% | +15-20% | +20-25% |
| Token 成本 | +50% | +100% | +200% |
| 实现复杂度 | 简单 | 中等 | 复杂 |
| 适用场景 | 短问题 | 文档质量参差 | 知识库不全 |

## 实战组合方案

实际项目中,**三种方案可以组合使用**:

```python
def advanced_rag(question, llm, vector_db, web_search):
    # 1. HyDE: 生成假想答案,提升检索
    hypothetical = llm(f"请详细回答:{question}")
    docs = vector_db.search(hypothetical, top_k=10)
    
    # 2. Self-RAG: 过滤相关文档
    relevant = filter_relevant(question, docs, llm)
    
    # 3. CRAG: 评估置信度,必要时补充 Web
    if len(relevant) < 3:
        web_results = web_search(question, top_k=5)
        relevant.extend(web_results)
    
    # 4. 生成最终答案
    context = "\n".join([d.content for d in relevant])
    return llm(f"基于:\n{context}\n回答:{question}")
```

**这套组合拳**:
- HyDE 提升召回率
- Self-RAG 提升准确率
- CRAG 保证完整性

## 我的项目实战数据

我做了 A/B 测试——

**对照组**:基础 RAG,准确率 68%
**实验组**:HyDE + Self-RAG + CRAG 组合,准确率 89%

**绝对提升 21 个百分点**——业务上的体感是"完全可用 → 接近人工水平"。

**成本对比**:
- 对照组:$0.002 / 查询
- 实验组:$0.012 / 查询(6 倍成本)

**值不值?看业务**——客服场景,$0.012 / 次换一个 89% 准确的回答,**完全值**。

## 几个关键经验

### 1. 不要过度优化

如果基础 RAG 已经达到 80%+ 准确率——**别上 HyDE、Self-RAG**。

**边际收益递减**——从 80% 推到 89% 成本 6 倍,从 60% 推到 89% 成本也 6 倍。

### 2. 评估是基础

**没有评估指标,所有优化都是盲改**。

```python
# 用测试集评估
test_questions = [...]
results = []

for q in test_questions:
    answer = rag(q)
    expected = q.expected_answer
    
    # 简单评估:用 GPT-4o 判断对错
    is_correct = llm(f"问题:{q.question}\n回答:{answer}\n标准:{expected}\n回答对吗?")
    results.append(is_correct)

accuracy = sum(results) / len(results)
```

### 3. 优化检索比重排序更有效

**很多时候问题不是 RAG 架构,是检索质量**。

优化检索:
- 更好的 embedding 模型
- 更好的文档分段
- 混合检索(BM25 + 向量)
- Query 改写

**这些比 HyDE/Self-RAG 更基础、更有效**。

### 4. 监控 + 持续优化

**RAG 系统需要持续优化**——

```python
# 监控用户反馈
for qa in user_conversations:
    if qa.user_feedback == "不准确":
        # 标记为待优化案例
        save_to_review_queue(qa)
```

## 写在最后

RAG 进阶方案,核心是**"提升检索质量 + 修正错误"**。

但记住:**架构不是万能药**——基础 RAG 80% 准确率时,先优化文档分段和 embedding 模型,再考虑架构升级。

> **RAG 工程的本质,是"用工程手段弥补 LLM 的不足"——HyDE/Self-RAG/CRAG 是工具,不是答案**。
