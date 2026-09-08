---
title: Agent 记忆系统——短期、长期、向量、图四种记忆怎么选
categories:
  - AI
tags:
  - Agent
  - 记忆
  - 向量数据库
  - 知识图谱
description: Agent 没有记忆就是个"金鱼"。短期、长期、向量、图四种记忆,各适合什么场景?
date: 2026-08-05 10:00:00
---

# Agent 记忆系统——短期、长期、向量、图四种记忆怎么选

> Agent 没有记忆就是个"金鱼"——聊 5 轮就忘。**短期、长期、向量、图四种记忆,各适合什么场景?**

## 为什么 Agent 需要记忆

LLM 本身**没有状态**——每次调用都是全新的。

```python
# 调用 1
r1 = llm("我叫张三")
# 返回:"你好,张三"

# 调用 2(完全独立的调用,模型不记得调用 1)
r2 = llm("我叫什么?")
# 返回:"抱歉,我不知道你的名字"
```

**Agent 必须自己管理"记忆"**——把对话历史存下来,需要时检索。

## 四种记忆的核心区别

### 1. 短期记忆(Short-term Memory)

**当前对话的所有消息**——存在内存或 Redis。

```python
class ShortTermMemory:
    def __init__(self, max_messages=20):
        self.messages = []
        self.max = max_messages
    
    def add(self, message):
        self.messages.append(message)
        if len(self.messages) > self.max:
            # 滑窗:删最早的
            self.messages.pop(0)
    
    def get(self):
        return self.messages
```

**特点**:
- 快(内存读取)
- 简单
- 会话结束就丢

**适用**:实时对话、多轮问答。

### 2. 长期记忆(Long-term Memory)

**跨会话的信息**——存在数据库。

```python
class LongTermMemory:
    def __init__(self, db):
        self.db = db  # SQLite / Postgres
    
    def save(self, user_id, key, value):
        self.db.execute(
            "INSERT INTO memories (user_id, key, value) VALUES (?, ?, ?)",
            (user_id, key, value)
        )
    
    def recall(self, user_id, key):
        return self.db.execute(
            "SELECT value FROM memories WHERE user_id=? AND key=?",
            (user_id, key)
        ).fetchone()
```

**特点**:
- 持久(会话结束还在)
- 按 user 隔离
- 适合存"用户偏好"

**适用**:用户画像、个性化设置、历史任务。

### 3. 向量记忆(Vector Memory)

**用 Embedding 检索的语义记忆**——存到向量数据库。

```python
from chromadb import Client

class VectorMemory:
    def __init__(self):
        self.client = Client()
        self.collection = self.client.create_collection("memories")
    
    def save(self, text, metadata={}):
        embedding = embed(text)
        self.collection.add(
            embeddings=[embedding],
            documents=[text],
            metadatas=[metadata],
            ids=[str(uuid4())]
        )
    
    def recall(self, query, top_k=5):
        embedding = embed(query)
        results = self.collection.query(
            query_embeddings=[embedding],
            n_results=top_k
        )
        return results["documents"]
```

**特点**:
- 语义检索(找到"意思相近"的)
- 不依赖精确关键词
- 适合存"对话片段"

**适用**:客服历史、相似案例检索、知识库。

### 4. 图记忆(Graph Memory)

**用知识图谱存实体关系**——节点 + 边。

```python
from neo4j import GraphDatabase

class GraphMemory:
    def __init__(self):
        self.driver = GraphDatabase.driver("bolt://localhost:7687")
    
    def save_relation(self, entity1, relation, entity2):
        with self.driver.session() as session:
            session.run(
                """
                MERGE (a:Entity {name: $e1})
                MERGE (b:Entity {name: $e2})
                MERGE (a)-[r:RELATION {type: $rel}]->(b)
                """,
                e1=entity1, e2=entity2, rel=relation
            )
    
    def query(self, entity):
        # 查询实体的所有关系
        ...
```

**特点**:
- 表达实体关系
- 支持复杂查询(多跳推理)
- 适合存"事实"

**适用**:企业知识图谱、医疗关系网络、推荐系统。

## 记忆的关键设计问题

### 1. 写什么

不是所有信息都值得记——**只记"未来会用到的"**:

| 记 | 不记 |
|---|---|
| 用户偏好(喜欢的食物) | 寒暄(你好、谢谢) |
| 关键事实(住址、生日) | 临时计算结果 |
| 决策依据(为什么选 A) | 工具返回的临时数据 |
| 异常情况(用户报错过) | 通用的常识 |

### 2. 什么时候写

三种时机:

- **每次都写**:实时同步,但容易冗余
- **任务结束时写**:总结后写入,信息精炼
- **定期写**:批处理,成本低

**推荐**:**任务结束时写**——LLM 总结本轮关键信息,再写入长期记忆。

```python
def on_task_complete(state):
    summary = llm(f"""
    请总结以下对话中的关键信息:
    {state['messages']}
    
    输出:
    - 用户偏好:...
    - 关键事实:...
    - 决策依据:...
    """)
    
    for item in summary.items:
        long_term_memory.save(user_id, item.key, item.value)
```

### 3. 怎么读

**不能每次都把所有记忆塞进 Prompt**——会爆 Token。

**关键是"检索"**:

```python
def get_relevant_memory(query, user_id):
    # 1. 从长期记忆里精确查
    exact = long_term_memory.recall(user_id, query)
    if exact:
        return exact
    
    # 2. 从向量记忆里语义查
    semantic = vector_memory.recall(query, top_k=5)
    return semantic
```

**实战经验**:**精确查优先,语义查兜底**——精确查更准。

### 4. 怎么忘

**记忆不能无限增长**——要定期清理。

三种遗忘策略:

- **时间衰减**:30 天前的记忆权重降低
- **访问频率**:长期不访问的记忆删除
- **重要性评分**:不重要的记忆主动删除

```python
def decay_memory(memory):
    # 1 个月没访问过 → 删除
    if memory.last_accessed < now() - timedelta(days=30):
        memory.delete()
```

**这是"记忆"和"存储"的区别——记忆是动态的,会遗忘**。

## 我的实战组合方案

### 客服 Agent 的记忆系统

```python
class CustomerServiceMemory:
    def __init__(self, user_id):
        self.user_id = user_id
        self.short_term = ShortTermMemory(max_messages=20)  # 当前对话
        self.long_term = LongTermMemory(db)                   # 用户偏好
        self.vector = VectorMemory()                            # 历史对话
    
    def process(self, user_input):
        # 1. 加载相关记忆
        relevant_history = self.vector.recall(user_input, top_k=3)
        user_prefs = self.long_term.recall_all(self.user_id)
        
        # 2. 拼 Prompt
        prompt = build_prompt(
            short_term=self.short_term.get(),
            relevant_history=relevant_history,
            user_prefs=user_prefs,
            user_input=user_input
        )
        
        # 3. 调用 LLM
        response = llm(prompt)
        
        # 4. 更新记忆
        self.short_term.add(user_input)
        self.short_term.add(response)
        
        return response
    
    def on_session_end(self):
        # 5. 总结写入长期记忆
        summary = summarize(self.short_term.get())
        self.long_term.save(self.user_id, "session_summary", summary)
        self.vector.add(summary)
```

**这套架构跑了半年**,**用户满意度提升 30%**。

## 几个常见误区

### 误区 1:记忆越多越好

错。**记忆太多,反而干扰模型**——把不相关的信息塞进去,模型会"分心"。

**只检索 Top 5-10 条相关记忆**。

### 误区 2:每次都重写整个记忆

错。**记忆是累加的,不是覆盖的**。

每次只新增,不修改旧的(除非明确说"忘了")。

### 误区 3:用向量记忆存所有东西

错。**向量记忆适合"语义检索",不适合"精确查找"**。

用户偏好、订单号这种**精确数据**应该用关系数据库。

### 误区 4:不清理过期记忆

错。记忆爆炸是真实问题——**定期清理是必须的**。

## 写在最后

Agent 的记忆系统,**不是"越多越好"——是"对的就够"**。

四种记忆各有适用场景:
- 短期:实时对话
- 长期:用户偏好
- 向量:相似案例
- 图:实体关系

**生产系统通常是"组合使用"**——没有银弹,只有组合。

> **好的 Agent 记忆,像人的记忆——会记、会忘、会找**。
