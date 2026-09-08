---
title: Docker 从入门到生产实践
categories:
  - Cloud Native
  - Docker
tags:
  - Docker
  - 容器化
  - 镜像优化
description: 从镜像构建到生产部署，梳理 Docker 落地的关键实践：分层缓存、镜像瘦身、资源限制与网络排查。
date: 2026-02-05 10:00:00
---

# Docker 从入门到生产实践

> Docker 的价值不在于"会跑一个容器"，而在于把"环境一致性"从口头承诺变成工程事实。本文聚焦真正影响生产环境的几个关键点。

## 镜像分层：缓存用对了，构建快 10 倍

Dockerfile 的每一行指令都会生成一层。构建缓存能否命中，取决于指令和上下文是否变化。

一个反面例子：

```dockerfile
# 差：每次代码变动都让 COPY 之后的层全部失效
FROM openjdk:17
COPY . /app
RUN mvn package
```

依赖下载是构建中最慢的环节，却每次都要重跑。正确做法是**先拷贝依赖清单，再拷贝源码**：

```dockerfile
FROM openjdk:17
WORKDIR /app
COPY pom.xml .
RUN mvn dependency:go-offline
COPY src ./src
RUN mvn package -DskipTests
```

依赖层只有在 `pom.xml` 变化时才重建，日常改动源码时构建秒级完成。

## 镜像瘦身：从 800MB 到 120MB

大镜像的问题不只是占磁盘，更影响部署速度——每台机器都要拉一遍。

瘦身三板斧：

1. **多阶段构建**：构建阶段用完整 JDK，运行阶段只留 JRE。
2. **选对基础镜像**：能用 `alpine` 或 `distroless` 就不用完整发行版。
3. **清理构建缓存**：`RUN` 里下载依赖后立刻清理包管理器缓存。

```dockerfile
# 构建阶段
FROM maven:3.9-eclipse-temurin-17 AS build
WORKDIR /app
COPY . .
RUN mvn package -DskipTests

# 运行阶段
FROM eclipse-temurin:17-jre-alpine
COPY --from=build /app/target/*.jar app.jar
ENTRYPOINT ["java", "-jar", "app.jar"]
```

## 资源限制：不加限制等于裸奔

容器默认能占用宿主机全部资源。生产环境必须显式限制：

```yaml
services:
  app:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2g
```

尤其要注意 JVM 容器。Java 8 及以下默认按宿主机内存算堆大小，容器内会触发 OOM。要么用 Java 10+ 的 `-XX:+UseContainerSupport`，要么显式指定 `-Xmx`。

## 网络排查的几个高频问题

- **容器能通外网、宿主机访问不了容器**：检查端口映射是否用了 `127.0.0.1` 绑定。
- **容器之间 ping 不通**：确认是否在同一自定义网络，默认 bridge 网络不支持容器名解析。
- **DNS 解析失败**：检查 `/etc/resolv.conf` 是否被正确注入。

## 小结

Docker 用起来简单，用好却需要理解分层、网络、资源限制这些底层机制。镜像构建优化和资源限制是两条最容易被忽视、却最影响生产稳定性的线。
