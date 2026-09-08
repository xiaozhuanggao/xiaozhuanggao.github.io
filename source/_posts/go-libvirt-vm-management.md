---
title: Go + KVM/libvirt 实现虚拟机管理
categories:
  - Go
  - Virtualization
tags:
  - Go
  - KVM
  - libvirt
  - 虚拟化
description: 记录用 Go 调用 libvirt 实现虚拟机创建、启动、停止与生命周期管理的实践，深入理解虚拟化底层机制。
date: 2026-05-21 10:00:00
---

# Go + KVM/libvirt 实现虚拟机管理

> 云平台最底层的核心，是让一台物理机"长出"多台虚拟机。这篇文章记录我用 Go 调用 libvirt 实现虚拟机生命周期管理的实践。

## 技术背景

做超融合私有云时，我们面对的核心问题是：如何把 KVM 的虚拟化能力封装成可编程的接口，供上层平台调用。

技术栈选型：

- **KVM**：Linux 内核级虚拟化，负责真正的 CPU/内存虚拟化
- **QEMU**：用户态设备模拟，配合 KVM 使用
- **libvirt**：虚拟化管理抽象层，统一管理 KVM/QEMU/LXC 等

Go 侧通过 `libvirt-go` 绑定，直接调用 libvirt 的 C API。

## 连接与发现

首先连接本机 libvirt 守护进程：

```go
conn, err := libvirt.NewConnect("qemu:///system")
if err != nil {
    log.Fatal(err)
}
defer conn.Close()

// 列出所有虚拟机
doms, _ := conn.ListAllDomains(libvirt.CONNECT_LIST_DOMAINS_ACTIVE)
```

## 创建虚拟机

创建虚拟机的核心是定义 XML 域配置：

```xml
<domain type='kvm'>
  <name>vm-001</name>
  <memory unit='GiB'>4</memory>
  <vcpu>2</vcpu>
  <devices>
    <disk type='file' device='disk'>
      <source file='/data/images/vm-001.qcow2'/>
    </disk>
    <interface type='bridge'>
      <source bridge='br0'/>
    </interface>
  </devices>
</domain>
```

Go 里定义并创建：

```go
domain, err := conn.DomainDefineXML(xmlConfig)
if err != nil {
    log.Fatal(err)
}
// 启动
domain.Create()
```

## 生命周期管理

虚拟机的状态机是理解虚拟化的关键：

```text
defined（已定义） → running（运行中） → paused（暂停）
                     ↑                ↓
                   stopped（已停止） ← shut off（关机）
```

Go 侧对应不同的操作：

```go
domain.Resume()   // 暂停 → 运行
domain.Suspend()  // 运行 → 暂停
domain.Shutdown() // 优雅关机
domain.Destroy()  // 强制断电（类似拔电源）
domain.Undefine() // 删除定义
```

一个关键区别：`Shutdown` 走的是操作系统内部的关机流程，需要虚拟机里装了对应的 agent；`Destroy` 是直接终止 QEMU 进程，相当于物理机拔电，可能丢数据。**生产环境要优先 Shutdown，Destroy 只在极端情况兜底。**

## 资源配置与热迁移

除了基本生命周期，还有两块重要的能力：

- **资源调整**：在线调整 CPU、内存（需配合 libvirt 的 `SetMemoryFlags` / `SetVcpusFlags`）
- **热迁移**：把运行中的虚拟机从一台物理机迁到另一台（`Migrate`），这是超融合高可用的基础

## 小结

用 Go 封装 libvirt，本质是把虚拟化的底层能力变成平台可编排的资源。真正值钱的不只是"能创建虚拟机"，而是理解虚拟化底层的运行机制——状态机、存储后端、网络模型，这些才是云平台稳定性的根基。
