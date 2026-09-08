---
title: K3s NodePort 为什么只有一个节点能访问
categories:
  - Troubleshooting
  - Kubernetes
tags:
  - K3s
  - 网络排障
  - Flannel
  - NodePort
description: 一次真实的 K3s 网络故障排查：NodePort 服务只有部分节点可访问，逐层定位到 Flannel 网络异常的全过程。
date: 2026-04-30 10:00:00
---

# K3s NodePort 为什么只有一个节点能访问

> 这类"诡异"的网络问题最能体现一个人的排障能力。本文完整记录一次 K3s NodePort 服务异常的真实排查过程。

## 问题现象

集群有 3 个节点，部署了一个 NodePort 类型的服务。理论上，通过任意节点的 NodePort 端口都能访问到这个服务。但实际情况是：

- 节点 A 上访问：正常 ✅
- 节点 B、C 上访问：超时 ❌

## 排查思路

遇到网络问题，先从**数据包路径**一层层排除。

### 第一层：服务本身是否正常

在节点 A 上访问正常，说明服务本身没问题。问题出在"跨节点"的链路。

### 第二层：NodePort 规则是否生效

```bash
iptables -t nat -L -n | grep -A 5 NODEPORT
```

检查发现 B、C 节点上的 NodePort 转发规则是有的，问题不在 iptables。

### 第三层：跨节点 Pod 网络

NodePort 流量进来后，最终要转发到 Pod。而 Pod 可能调度在别的节点上，流量要经过**跨节点的容器网络**（Flannel 隧道）。

在 B 节点上 ping Pod IP，发现**不通**。基本锁定是 Flannel 网络问题。

### 第四层：定位 Flannel

```bash
# 查看 Flannel 分配的网段
kubectl get nodes -o jsonpath='{.items[*].spec.podCIDR}'

# 查看 Flannel 接口
ip a | grep flannel
```

最终发现：B、C 节点的 Flannel 接口正常，但**路由表缺失了指向其他节点 Pod 网段的路由**，导致跨节点流量没有走隧道，而是走了默认路由然后被丢弃。

## 根因与修复

根因是 Flannel 节点间的路由信息没有同步完整（通常和节点加入集群时的初始化异常有关）。修复方式：

```bash
# 重启 flannel，重新同步路由
kubectl -n kube-system rollout restart daemonset kube-flannel
```

重启后 Flannel 重新下发路由，B、C 节点的 NodePort 访问恢复正常。

## 小结

网络问题排查的核心方法是**分层定位**：从应用层到 NodePort 规则，再到跨节点 Pod 网络，一层层排除。这次的教训是——**NodePort 能在一个节点通、其他节点不通，问题几乎一定在跨节点的容器网络层**，而不是应用本身。
