---
title: 大模型应用开发基础：API 调用与工程封装
categories:
  - AI
  - LLM
tags:
  - LLM
  - OpenAI
  - DeepSeek
  - API 封装
description: 从最基础的 API 调用开始，梳理大模型应用开发的工程封装：流式输出、重试、多模型抽象与成本控制。
date: 2026-05-28 10:00:00
---

# 大模型应用开发基础：API 调用与工程封装

> 这是我系统转向 AI 应用开发的第一篇笔记。一切从"调用一次大模型 API"开始，但真正要落地，靠的是工程封装。

## 一次最简调用

调一个大模型 API 本质上就是发一个 HTTP 请求：

```python
import requests

resp = requests.post(
    "https://api.deepseek.com/v1/chat/completions",
    headers={"Authorization": "Bearer sk-xxx"},
    json={
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": "你好"}],
    },
)
print(resp.json()["choices"][0]["message"]["content"])
```

看起来简单，但真正要把它用进业务系统，有四个必须解决的问题。

## 问题一：流式输出

长回答如果等完整生成，用户要盯着白屏几十秒。**流式输出（stream）**是必备能力：

```python
json["stream"] = True
for chunk in resp:
    delta = chunk["choices"][0]["delta"].get("content", "")
    yield delta  # 逐步返回给前端
```

## 问题二：失败重试

大模型 API 会有超时、限流、服务不稳定。工程上必须做**指数退避重试**：

```python
for attempt in range(3):
    try:
        return call_llm(...)
    except RateLimitError:
        time.sleep(2 ** attempt)  # 1s, 2s, 4s
```

## 问题三：多模型抽象

不同厂商（OpenAI、DeepSeek、Qwen）接口大同小异，但细节有差异。与其散落一堆 if-else，不如抽象一层统一接口：

```python
class LLMClient:
    def chat(self, messages, stream=False) -> str: ...
    def embed(self, text) -> list[float]: ...

# 各厂商各自实现，业务代码只依赖 LLMClient
```

这样切换模型、灰度对比新模型都只改配置，不动业务。

## 问题四：Token 与成本

Token 是钱。开发时就要关注：

- **上下文窗口**：长对话要截断或摘要，避免 token 爆炸
- **缓存**：相同前缀的请求命中 KV Cache 可以省钱
- **选模型**：简单任务用便宜的小模型，复杂任务才上大模型

## 小结

"会调 API"和"能工程化落地"之间的差距，就是这四件事：流式、重试、抽象、成本。把地基打好，后面做 RAG、Agent 才不至于返工。
