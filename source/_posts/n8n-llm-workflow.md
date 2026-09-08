---
title: AI 工作流自动化——n8n + LLM 实战
categories:
  - AI
tags:
  - AI工作流
  - n8n
  - 自动化
  - 工具
description: 把 AI 嵌入工作流,自动化重复任务。n8n + LLM 是 2025 年最强组合。
date: 2026-08-26 10:00:00
---

# AI 工作流自动化——n8n + LLM 实战

> 把 AI 嵌入工作流,自动化重复任务。**n8n + LLM 是 2025 年最强组合**。

## 什么是 AI 工作流自动化

**AI 工作流 = 多个工具 + LLM + 自动化编排**。

经典场景:
- 用户提交工单 → AI 自动分类 → 分配给对应团队 → 通知 Slack
- RSS 新文章 → AI 摘要 → 发到 Discord → 归档到 Notion
- 邮件新消息 → AI 判断重要性 → 紧急的发短信,普通的归档

**核心**:AI 不替代人,而是**嵌在流程的"决策点"上**。

## 为什么选 n8n

### 主流工作流工具对比

| 工具 | 开源 | AI 集成 | 易用性 | 成本 |
|---|---|---|---|---|
| n8n | ✅ | ✅ 原生 | 中 | 免费(自部署) |
| Zapier | ❌ | ✅ | 高 | $20+/月 |
| Make | ❌ | ✅ | 中 | $10+/月 |
| Dify | ✅ | ✅ 极强 | 中 | 免费 |
| Coze | ❌ | ✅ | 高 | 免费 |

**n8n 的优势**:
- 开源、可私有部署
- 400+ 集成(几乎所有主流工具)
- AI 节点原生支持
- 可视化编排,逻辑清晰
- 自部署免费

**n8n 的局限**:
- 学习曲线比 Zapier 陡
- 复杂逻辑需要懂 JS/Python

## 第一个 AI 工作流:工单自动分类

### 场景

客服系统收到工单:
1. AI 自动读工单内容
2. 判断属于哪个类别(技术支持、账单、退款、其他)
3. 自动分配给对应团队 Slack 频道
4. 紧急工单发短信通知

### 搭建步骤

#### 1. 启动 n8n

```bash
docker run -it --rm \
  --name n8n \
  -p 5678:5678 \
  -v ~/.n8n:/home/node/.n8n \
  n8nio/n8n
```

打开 `http://localhost:5678`。

#### 2. 创建 Workflow

**节点 1:Webhook 触发**
- 监听 HTTP POST `/webhook/new-ticket`
- 接收工单数据:`{title, content, user_email, ...}`

**节点 2:AI Agent(LLM 分类)**

```javascript
// n8n AI Agent 配置
{
  "model": "gpt-4o-mini",
  "systemPrompt": `你是客服分类员,根据工单内容判断类别。
  
  类别:
  - tech_support: 技术问题、Bug、故障
  - billing: 账单、发票、付款
  - refund: 退款、取消
  - other: 其他
  
  输出 JSON:{"category": "...", "urgency": "high|medium|low", "summary": "..."}`,
  "input": "{{ $json.content }}"
}
```

**节点 3:Switch 节点(按类别分支)**

```
if category == "tech_support" → Slack 频道 #tech-support
if category == "billing" → Slack 频道 #billing
...
```

**节点 4:Slack 通知**

```javascript
{
  "channel": "#tech-support",
  "text": `🆕 新工单\n标题:{{ $json.title }}\n摘要:{{ $json.summary }}\n紧急度:{{ $json.urgency }}`
}
```

**节点 5:紧急工单发短信**

```javascript
if urgency == "high":
    // 调用 Twilio API 发短信
    await twilio.messages.create({
        to: "+86...",
        from: "+1...",
        body: `紧急工单:{{ $json.title }}`
    })
```

#### 3. 测试

用 curl 触发:
```bash
curl -X POST http://localhost:5678/webhook/new-ticket \
  -H "Content-Type: application/json" \
  -d '{"title": "App 不能登录", "content": "用户登录后白屏..."}'
```

**观察流程**:
1. Webhook 接收
2. LLM 分类:`tech_support` + `high`
3. 发到 #tech-support
4. 发短信通知 on-call

**完成**——整个流程不到 30 秒。

## 进阶:RSS 摘要自动推送到 Discord

### 场景

我订阅了 20 个技术博客 RSS,每天 100+ 新文章,读不完。

**用 n8n + LLM 自动**:
- 每小时抓取新文章
- AI 生成中文摘要
- 推送到 Discord 频道

### 搭建

**节点 1:Schedule Trigger**
- 每小时执行一次

**节点 2:RSS Feed Read**
- 读取多个 RSS:`https://blog1.com/feed`, `https://blog2.com/feed`...

**节点 3:Code 节点(过滤已读)**
```python
# 用 Redis 或 n8n 内置存储记录已读文章
seen = get_seen_articles()
new_articles = [a for a in articles if a.id not in seen]
```

**节点 4:Loop Over Items**
- 遍历每篇新文章

**节点 5:AI 摘要**

```javascript
{
  "model": "claude-haiku",
  "systemPrompt": "你是一个技术内容摘要员,把英文技术文章摘要成 200 字中文。",
  "input": "{{ $json.content }}"
}
```

**节点 6:Discord 发送**

```javascript
{
  "channel": "#tech-feed",
  "embed": {
    "title": "{{ $json.title }}",
    "url": "{{ $json.url }}",
    "description": "{{ $json.summary }}",
    "color": 0x00ff00
  }
}
```

### 效果

- 每天自动收 20-30 篇精选摘要
- 不再被 RSS 淹没
- **节省 1 小时/天**

## 进阶:邮件智能分流

### 场景

每天 50+ 邮件,大部分是通知/广告。

**用 n8n 自动化**:
- 紧急邮件(老板、客户)→ 短信 + 推送
- 一般邮件 → Slack
- 广告邮件 → 直接归档

### 搭建

**节点 1:Email Trigger(IMAP)**
- 每 5 分钟拉新邮件

**节点 2:AI 判断**

```javascript
{
  "model": "gpt-4o-mini",
  "systemPrompt": `判断邮件重要性。
  
  输出 JSON:
  {
    "importance": "critical|important|normal|spam",
    "reason": "...",
    "action": "sms|slack|archive"
  }`,
  "input": `发件人:{{ $json.from }}\n主题:{{ $json.subject }}\n内容:{{ $json.body }}`
}
```

**节点 3:Switch 分流**

```
if importance == "critical" → Twilio 短信 + Slack @channel
if importance == "important" → Slack 普通消息
if importance == "spam" → 邮件归档到 Spam 文件夹
```

### 效果

- 紧急邮件 **秒级** 响应
- 不再被邮件淹没
- 每天节省 30 分钟

## 进阶:Notion 知识库自动整理

### 场景

我在 Notion 记了大量笔记,但懒得整理。

**用 n8n 自动化**:
- 每周扫一次 Notion 未分类笔记
- AI 自动打标签、归类
- 推送周报到 Slack

### 搭建

**节点 1:Schedule Trigger**
- 每周一 9 点

**节点 2:Notion Query**
- 查询 `category is empty`

**节点 3:AI 分类**

```javascript
{
  "model": "claude-sonnet",
  "systemPrompt": `你是笔记整理助手,根据内容给笔记打标签、归类。
  
  类别:技术、产品、生活、阅读、灵感
  标签:具体关键词
  
  输出 JSON:{category, tags, summary}`,
  "input": "{{ $json.content }}"
}
```

**节点 4:Notion Update**
- 更新笔记的 category 和 tags

**节点 5:Slack 周报**

```javascript
{
  "text": `📚 本周整理笔记 {{ $json.count }} 篇\n分类分布:...`
}
```

## n8n 的高级用法

### 1. 错误处理

每个节点都可以配置 **"on error"**:
- 继续执行
- 停止工作流
- 跳到错误分支

```javascript
// 节点配置
{
  "onError": "continueRegularOutput",
  "retryOnFail": true,
  "maxTries": 3,
  "waitBetweenTries": 1000
}
```

### 2. 变量与表达式

n8n 支持表达式语言:
- `{{ $json.field }}`:取数据
- `{{ $now }}`:当前时间
- `{{ $env.API_KEY }}`:环境变量

### 3. Code 节点(自定义逻辑)

复杂逻辑用 Code 节点(支持 JS / Python):

```javascript
// JavaScript Code 节点
const items = $input.all();
const grouped = {};

for (const item of items) {
    const category = item.json.category;
    if (!grouped[category]) {
        grouped[category] = [];
    }
    grouped[category].push(item.json);
}

return Object.entries(grouped).map(([category, items]) => ({
    json: { category, count: items.length, items }
}));
```

### 4. 子工作流

**复杂工作流拆成多个子工作流**——可复用、可维护。

## 几个实战经验

### 1. 简单优先

**不要一上来就搞复杂**——先做"能用的最小版本",再迭代。

我的第一个工作流只有 3 个节点,跑了半年,后来才加复杂度。

### 2. 监控 + 告警

**工作流挂了,你不知道——这是最危险的**。

```javascript
// 在关键节点后加 Slack 通知
{
  "channel": "#ops-alert",
  "text": `⚠️ Workflow {{ $workflow.name }} failed at node {{ $node.name }}`
}
```

### 3. 限流

**别让工作流无限循环**——LLM 调用是按 Token 算钱的。

```javascript
// 限流:每分钟最多 10 次
{
  "rateLimit": {
    "maxRequests": 10,
    "perInterval": 60000
  }
}
```

### 4. 数据持久化

工作流运行数据存在 n8n 数据库,**但生产环境要备份**。

```bash
# n8n 数据备份
docker exec n8n n8n export:workflow --all --output=/backups/workflows.json
```

## 写在最后

AI 工作流自动化,核心是**"让 AI 做决策,让人做最终动作"**。

n8n 是目前最适合的工具——
- 集成丰富
- AI 原生
- 可私有化

我的建议:
- **从简单工作流开始**(3-5 个节点)
- **用 AI 替代决策节点**(分类、摘要、判断)
- **保留人工入口**(重要决策人工 review)

> **AI 工作流的本质,是"把人从重复决策中解放出来"——不是"完全自动化",是"半自动化"**。
