---
title: K3s 轻量级集群搭建与踩坑
categories:
  - Cloud Native
  - K3s
tags:
  - K3s
  - Kubernetes
  - 云原生
description: 记录 K3s 集群从零搭建到承载生产服务的完整过程，以及踩过的几个典型坑。
date: 2026-04-02 10:00:00
---

# K3s 轻量级集群搭建与踩坑

> 对很多中小规模团队来说，完整 Kubernetes 太重，K3s 是更现实的选择。本文记录我在政企内网环境搭建 K3s 集群并承载生产服务的完整过程。

## 为什么选 K3s

我们面临的环境是：内网隔离、机器资源有限（几台普通服务器）、没有专职 SRE。在这种条件下：

- 完整 K8s 的 etcd、控制面组件开销大、维护成本高
- K3s 把控制面打包成单个二进制，默认用 SQLite 存数据，资源占用极低

更重要的是，K3s 保留了标准 Kubernetes API，业务上的编排能力一点不少。

## 搭建过程

安装本身非常简单：

```bash
# 主节点
curl -sfL https://get.k3s.io | sh -

# 查看节点 token，供 worker 加入
cat /var/lib/rancher/k3s/server/node-token
```

worker 节点加入：

```bash
curl -sfL https://get.k3s.io | K3S_URL=https://<master-ip>:6443 \
  K3S_TOKEN=<node-token> sh -
```

## 踩坑记录

### 坑一：内网无法访问 get.k3s.io

政企内网往往没有外网，安装脚本拉不下来。解法是**离线安装**：提前下载 K3s 二进制和 airgap 镜像包，内网里用 `INSTALL_K3S_SKIP_DOWNLOAD=true` 指定本地文件。

### 坑二：默认 Traefik 和业务 Ingress 冲突

K3s 默认自带 Traefik。如果团队习惯用 Nginx Ingress，需要安装时关掉 Traefik，避免两套 Ingress Controller 争抢。

### 坑三：镜像拉取失败

内网环境跑 `docker pull` 不通，需要配置私有镜像仓库（Harbor），并把业务镜像推到内网仓库，Pod 里用内网地址拉取。

### 坑四：cgroup 版本问题

老内核是 cgroup v1，新版容器运行时默认 v2，导致 Pod 资源限制不生效。需要在启动参数里显式指定 cgroup 驱动，保持一致。

## 小结

K3s 的上手成本比想象中低，但"能用"和"生产可用"之间隔着离线安装、Ingress 冲突、镜像源、cgroup 这些具体的坑。把这些坑踩平，K3s 是中小团队落地云原生性价比最高的选择之一。
