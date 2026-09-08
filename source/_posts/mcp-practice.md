---
title: MCP(Model Context Protocol)实战——AI 工具集成的新标准
categories:
  - AI
tags:
  - MCP
  - Agent
  - 工具集成
  - 协议
description: MCP 是 Anthropic 推出的"AI 时代的 USB-C"。一次接入,所有模型都能用。
date: 2026-08-23 10:00:00
---

# MCP(Model Context Protocol)实战——AI 工具集成的新标准

> MCP 是 Anthropic 推出的"AI 时代的 USB-C"。**一次接入,所有模型都能用**。

## 什么是 MCP

**Model Context Protocol(MCP)** 是 2024 年底由 Anthropic 开源的协议。

**核心思想**:为 AI 模型和外部工具/数据之间,定义**统一标准**。

类比 USB-C:
- 以前:每个设备要单独接各种线(HDMI、VGA、DP...)
- 现在:**一个 USB-C 接所有**
- MCP = **AI 工具的 USB-C**

## MCP 解决了什么问题

### 之前:每个模型都要单独集成工具

```
GPT-4o 调工具:用 OpenAI 的 function calling 格式
Claude 调工具:用 Anthropic 的 tool use 格式
Gemini 调工具:用 Google 的格式
...
```

**问题**:
- 写一个工具,要在多个 SDK 里写多份
- 模型切换成本高
- 工具生态割裂

### 现在:MCP 统一接口

```
工具开发者:写一份 MCP server
所有模型:都能调
```

**一次开发,处处运行**。

## MCP 的核心组件

### 1. MCP Server(服务端)

**暴露工具和数据**——可以是本地进程,也可以是远程服务。

```python
# example_mcp_server.py
from mcp.server import Server
from mcp.types import Tool, TextContent

app = Server("my-tools")

@app.tool()
async def get_weather(city: str) -> list[TextContent]:
    """查询指定城市的天气"""
    weather = await fetch_weather_from_api(city)
    return [TextContent(
        type="text",
        text=f"{city}今天:{weather}"
    )]

@app.tool()
async def search_docs(query: str) -> list[TextContent]:
    """搜索内部文档"""
    results = await search_internal_docs(query)
    return [TextContent(type="text", text="\n".join(results))]
```

### 2. MCP Client(客户端)

**MCP 客户端可以是 Claude Desktop、Cursor 这样的 AI 应用**。

```python
from mcp.client import Client

async with Client("stdio://example_mcp_server.py") as client:
    # 列出所有工具
    tools = await client.list_tools()
    print(tools)
    
    # 调用工具
    result = await client.call_tool("get_weather", {"city": "上海"})
    print(result)
```

### 3. 传输协议

MCP 支持多种传输:
- **stdio**:本地进程(最常用)
- **HTTP+SSE**:远程服务
- **WebSocket**:双向通信

## 实战:写一个 MCP Server

### 场景

我需要让 AI 能查询我的:
- 飞书日历
- 内部 GitLab
- 自定义数据库

### Step 1:安装 SDK

```bash
pip install mcp
```

### Step 2:写 MCP Server

```python
import asyncio
from mcp.server import Server
from mcp.types import Tool, TextContent
import httpx

app = Server("work-tools")

@app.tool(
    name="query_database",
    description="查询内部数据库,支持简单 SQL",
    parameters={
        "type": "object",
        "properties": {
            "sql": {"type": "string", "description": "SQL 查询语句"}
        },
        "required": ["sql"]
    }
)
async def query_database(sql: str) -> list[TextContent]:
    """查询内部数据库"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://db.internal/api/query",
            json={"sql": sql},
            headers={"Authorization": "Bearer xxx"}
        )
        data = response.json()
        return [TextContent(type="text", text=str(data))]

@app.tool(
    name="create_meeting",
    description="创建飞书日历会议",
    parameters={
        "type": "object",
        "properties": {
            "title": {"type": "string"},
            "start_time": {"type": "string", "description": "ISO 格式"},
            "duration_minutes": {"type": "integer"},
            "attendees": {"type": "array", "items": {"type": "string"}}
        },
        "required": ["title", "start_time"]
    }
)
async def create_meeting(title: str, start_time: str, duration_minutes: int = 60, attendees: list = []) -> list[TextContent]:
    """创建飞书日历会议"""
    # 调飞书 API
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://open.feishu.cn/open-apis/calendar/v4/calendars/events",
            json={
                "summary": title,
                "start_time": start_time,
                "duration": duration_minutes,
                "attendees": attendees
            },
            headers={"Authorization": "Bearer xxx"}
        )
        return [TextContent(type="text", text=f"会议创建成功:{response.json()}")]

async def main():
    # 启动 MCP server
    from mcp.server.stdio import stdio_server
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
```

### Step 3:配置 Claude Desktop

编辑 `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "work-tools": {
      "command": "python",
      "args": ["/path/to/example_mcp_server.py"]
    }
  }
}
```

重启 Claude Desktop,**"work-tools" 的两个工具就出现在工具列表里**。

### Step 4:让 Claude 用

直接在 Claude Desktop 里说:
- "查一下用户表的最近 10 条记录"
- "创建一个会议,明天上午 10 点,主题是产品 review"

Claude 会**自动发现并调用 MCP 工具**。

## MCP 的实际价值

### 价值 1:工具复用

**写一次,所有 AI 应用都能用**。

我写了一个"查天气"的 MCP server:
- Claude Desktop 能用
- Cursor 能用
- 自定义 Agent 能用

### 价值 2:生态丰富

**Anthropic 推出了官方 MCP 仓库**,已经有 100+ 社区 MCP server:
- GitHub MCP(操作 GitHub)
- Slack MCP(发消息)
- Notion MCP(读 Notion)
- 数据库 MCP(查 SQL)
- 文件系统 MCP(操作本地文件)

**直接拿来用,不用自己写**。

### 价值 3:标准化

以前每个 Agent 框架都有自己的工具定义(LangChain Tools、AutoGen Functions...)。

**现在统一用 MCP**——工具迁移成本接近 0。

### 价值 4:安全性

**MCP Server 可以控制权限**——

```python
@app.tool()
async def dangerous_operation(action: str):
    if not user_has_permission():
        raise PermissionError("无权操作")
    # ...
```

**比直接暴露 API 安全得多**。

## MCP vs Function Calling

| 维度 | Function Calling | MCP |
|---|---|---|
| 模型绑定 | 绑定具体模型 | 模型无关 |
| 工具定义 | 各家不同 | 统一标准 |
| 复用 | 难 | 易 |
| 生态 | 各自 | 共享 |
| 适用 | 单一应用 | 多应用场景 |

**结论**:
- 单应用、单模型 → Function Calling
- 多应用、多模型 → MCP

## MCP 的局限

### 1. 还在早期

**MCP 协议 2024 年 11 月才发布**——生态还不够丰富。

很多场景还得自己写 MCP server。

### 2. 性能开销

MCP 通过 stdio / HTTP 通信,**比直接 function calling 多一层序列化**。

高频工具调用时,**延迟增加 10-50ms**。

### 3. 复杂场景不友好

多步骤、有状态的工具——MCP 不太合适,**还是要用 LangGraph 那种框架**。

### 4. 模型支持有限

目前主要 Claude Desktop / Cursor 支持较好。

GPT、Gemini 等其他模型对 MCP 的支持还在跟进中。

## 我的实战项目

### 项目 1:个人 AI 助手

我写了一个 MCP server,集成了:
- 飞书日历(创建会议)
- 内部 Wiki(查文档)
- 监控系统(查服务状态)

**每天节省 30 分钟**——以前手动操作,现在 Claude 自动做。

### 项目 2:团队工具集成

给团队写了一个 MCP server,集成:
- GitLab(创建 MR、查 issue)
- 数据库(查 SQL)
- 部署系统(触发部署)

**全团队都在用**——Claude Desktop 直接调这些工具,不用切窗口。

## 几个最佳实践

### 1. Tool Description 要写清楚

```python
@app.tool(
    name="query_database",
    description="""查询内部业务数据库。
    
    适用场景:
    - 查用户、订单、产品等业务数据
    - 简单的 SELECT 查询
    
    不适用:
    - 写操作(INSERT/UPDATE/DELETE)
    - 复杂 JOIN(>3 个表)
    - 大数据量(>1 万行)
    
    必须传 SQL 参数,例如 'SELECT * FROM users LIMIT 10'
    """
)
```

**模型靠 description 决定调不调——写清楚最重要**。

### 2. 错误处理要友好

```python
@app.tool()
async def query_database(sql: str):
    try:
        result = await execute_sql(sql)
        return [TextContent(type="text", text=str(result))]
    except Exception as e:
        # 返回错误信息,模型能看到并修正
        return [TextContent(type="text", text=f"错误:{str(e)}")]
```

**不要 raise 异常——返回错误文本,让模型理解并修正**。

### 3. 参数验证

```python
@app.tool()
async def create_meeting(title: str, start_time: str):
    # 验证参数
    try:
        dt = datetime.fromisoformat(start_time)
    except ValueError:
        return [TextContent(type="text", text="start_time 格式错误,需要 ISO 格式如 '2026-08-23T10:00:00'")]
    
    # ...
```

**提前验证参数,避免错误传到下游**。

### 4. 日志记录

```python
import logging
logger = logging.getLogger(__name__)

@app.tool()
async def query_database(sql: str):
    logger.info(f"SQL query: {sql}")
    result = await execute_sql(sql)
    logger.info(f"Result rows: {len(result)}")
    return [TextContent(type="text", text=str(result))]
```

**没有日志,出问题就是黑盒**。

## 写在最后

MCP 是 AI 工具集成领域**最值得关注的协议**——它的目标是"统一标准",**这个方向是对的**。

短期内,Function Calling 仍是主流;
长期看,MCP 可能成为**AI 工具的事实标准**。

我的建议:
- **学习 MCP**——未来 1-2 年会越来越重要
- **写自己的 MCP Server**——哪怕只是小工具
- **关注生态发展**——Anthropic 在大力推

> **MCP 的本质,是"为 AI 时代的工具集成提供基础设施"——就像 USB-C 为硬件做的一样**。
