---
title: Kubernetes 入门与生产实践
categories:
  - Cloud Native
  - Kubernetes
tags:
  - Kubernetes
  - Docker
  - 云原生
description: 从零讲解 Kubernetes 核心概念，并分享生产环境的部署、调优经验。
abbrlink: 3cfbd3fc
date: 2026-05-07 10:00:00
---

# Kubernetes 入门与生产实践

> Kubernetes 是云原生时代的事实标准。本文从核心概念到生产部署，系统梳理 K8s 学习路径。

## 核心概念

```text
Pod（最小部署单元）
   ↓
Deployment（无状态部署）
   ↓
StatefulSet（有状态部署）
   ↓
Service（服务发现）
   ↓
Ingress（外部入口）
   ↓
ConfigMap / Secret（配置管理）
```

## 为什么需要 K8s

- **自动伸缩**：HPA 根据 CPU/内存/自定义指标扩缩容
- **自愈能力**：Pod 异常自动重启
- **滚动更新**：零停机发布
- **资源隔离**：namespace + resource quota

## 生产部署要点

### 1. 资源 requests / limits

```yaml
resources:
  requests:
    cpu: 100m
    memory: 128Mi
  limits:
    cpu: 500m
    memory: 512Mi
```

### 2. 健康检查

- **livenessProbe**：存活探针
- **readinessProbe**：就绪探针
- **startupProbe**：启动探针（慢启动服务）

### 3. 配置管理

- ConfigMap 存非敏感配置
- Secret 存敏感配置
- 避免在镜像中硬编码

### 4. 网络

- Calico / Cilium 网络插件
- NetworkPolicy 限制 Pod 间访问

## 常见坑

| 问题 | 解决 |
|------|------|
| Pod 频繁重启 | 排查 liveness 探针 / 资源 limits |
| 服务无法访问 | 检查 Service / Endpoints / DNS |
| 镜像拉取失败 | 检查 imagePullSecrets |
| PVC 一直 Pending | 检查 StorageClass |

## 总结

K8s 学习曲线陡峭，但掌握后能极大提升运维效率。本站后续会持续更新 K8s 实战内容。