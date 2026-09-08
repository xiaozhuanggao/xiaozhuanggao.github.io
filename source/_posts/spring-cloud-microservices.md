---
title: Spring Cloud 微服务架构演进
categories:
  - Java
  - Spring Cloud
tags:
  - Spring Boot
  - Spring Cloud
  - 微服务
description: 总结 Spring Cloud 微服务架构的演进路径、组件选型与踩坑经验。
abbrlink: 16b97a34
date: 2026-01-22 10:00:00
---

# Spring Cloud 微服务架构演进

> 从单体到微服务，是企业级系统架构演进的必经之路。本文梳理 Spring Cloud 微服务的核心组件与实战经验。

## 演进路径

```text
单体应用
   ↓
垂直拆分（按业务）
   ↓
SOA（服务化）
   ↓
微服务（独立部署、独立伸缩）
```

## Spring Cloud 核心组件

| 组件 | 职责 |
|------|------|
| Eureka / Nacos | 服务注册与发现 |
| Config / Nacos | 配置中心 |
| Gateway / Zuul | API 网关 |
| OpenFeign / RestTemplate | 服务调用 |
| Hystrix / Sentinel | 熔断限流 |
| Sleuth / SkyWalking | 链路追踪 |

## 选型建议

- **新项目**：Spring Cloud Alibaba（Nacos + Sentinel + Seata）
- **存量项目**：Spring Cloud Netflix（Hystrix 已停止维护，注意迁移）

## 微服务 ≠ 银弹

引入微服务带来的复杂度：

1. 分布式事务
2. 链路追踪
3. 服务治理
4. 部署复杂度
5. 测试复杂度

**判断标准**：业务复杂度 / 团队规模 / 部署频率 三者同时具备，再考虑微服务。

## 总结

Spring Cloud 是 Java 生态微服务的成熟方案，但不要为了"上微服务而上微服务"。本站后续会持续更新 Spring Cloud 实战内容。