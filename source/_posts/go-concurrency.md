---
title: Go 并发编程：goroutine 与 channel
categories:
  - Go
  - Concurrency
tags:
  - Go
  - 并发
  - 协程
description: 系统讲解 Go 语言的 goroutine、channel 与并发模式。
abbrlink: 4c4d6972
date: 2026-05-14 10:00:00
---

# Go 并发编程：goroutine 与 channel

> Go 语言以简洁的并发模型著称。本文梳理 goroutine 与 channel 的核心用法。

## goroutine

启动一个 goroutine 非常简单：

```go
go func() {
    fmt.Println("hello from goroutine")
}()
```

注意：

- `main` 结束时不会等待 goroutine 完成
- goroutine 泄漏是常见 bug

## channel

### 无缓冲 channel

```go
ch := make(chan int)
go func() {
    ch <- 42  // 阻塞直到有接收者
}()
fmt.Println(<-ch)  // 阻塞直到有数据
```

### 有缓冲 channel

```go
ch := make(chan int, 3)
ch <- 1
ch <- 2
// 不会阻塞
```

## 常用并发模式

### 1. Worker Pool

```go
jobs := make(chan int, 100)
results := make(chan int, 100)

for w := 1; w <= 3; w++ {
    go worker(w, jobs, results)
}

for j := 1; j <= 5; j++ {
    jobs <- j
}
close(jobs)

for a := 1; a <= 5; a++ {
    <-results
}
```

### 2. select 多路复用

```go
select {
case msg := <-ch1:
    fmt.Println(msg)
case <-time.After(1 * time.Second):
    fmt.Println("timeout")
}
```

### 3. context 取消

```go
ctx, cancel := context.WithCancel(context.Background())
go func() {
    select {
    case <-ctx.Done():
        return
    case <-ch:
        // do work
    }
}()
cancel()
```

## 常见陷阱

| 陷阱 | 解决 |
|------|------|
| goroutine 泄漏 | 用 context 控制生命周期 |
| 数据竞争 | 用 sync.Mutex 或 channel |
| 死锁 | 注意 channel 收发的对应 |

## 总结

Go 的并发模型哲学是"通过通信来共享内存，而不是通过共享内存来通信"。本站后续会持续更新 Go 并发实战内容。