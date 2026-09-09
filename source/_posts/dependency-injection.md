---
title: 依赖注入：为什么你的代码不该自己 new 对象
categories:
  - 基础
tags:
  - 设计模式
  - 依赖注入
  - Spring
  - 架构
description: 依赖注入是 SOLID 原则里依赖倒置的落地，也是 Spring 的核心机制。这篇讲清楚控制反转、构造器注入，以及 DI 到底解决了什么问题。
date: 2026-02-02 10:00:00
---

上一篇讲 SOLID 时，最后一条"依赖倒置原则（DIP）"是最难的。而**依赖注入（DI）就是 DIP 的落地实现**。

如果你用过 Spring，那你天天都在用 DI，只是可能没想过它背后的道理。

## 没有 DI 的世界

先看一段"正常"的代码：

```java
public class OrderService {
    private OrderRepository repository = new MySQLOrderRepository();
    private EmailSender emailSender = new SmtpEmailSender();
}
```

这段代码有什么问题？

1. **强耦合**：`OrderService` 直接依赖了具体实现 `MySQLOrderRepository`。要换数据库，就得改 `OrderService`。
2. **难测试**：想测试 `OrderService`，没法单独测，因为它内部硬绑定了真实的数据库和邮件服务。
3. **重复创建**：每个用到 `OrderRepository` 的类都自己 `new` 一个，浪费资源且状态难统一。

## 依赖注入的解法

DI 的思路是：**对象不再自己创建它的依赖，而是由外部把依赖"注入"进来**。

```java
public class OrderService {
    private final OrderRepository repository;
    private final EmailSender emailSender;

    // 依赖通过构造函数注入
    public OrderService(OrderRepository repository, EmailSender emailSender) {
        this.repository = repository;
        this.emailSender = emailSender;
    }
}
```

现在 `OrderService` 只依赖接口 `OrderRepository`，不关心具体是谁来实现。这个"谁"，由外部决定。

**这就是"控制反转（IoC）"**：创建依赖的控制权，从"类自己"反转到了"外部"。

## 三种注入方式

### 1. 构造器注入（推荐）

```java
public OrderService(OrderRepository repository) {
    this.repository = repository;
}
```

- 优点：依赖在构造时就必须提供，对象创建出来就是"完整可用"的，不会漏
- 缺点：依赖多时构造函数参数很长

### 2. Setter 注入

```java
public void setRepository(OrderRepository repository) {
    this.repository = repository;
}
```

- 优点：灵活，可选的依赖适合用这种
- 缺点：可能忘记调用 setter，导致对象状态不完整

### 3. 字段注入（不推荐）

```java
@Autowired
private OrderRepository repository;
```

Spring 提供了 `@Autowired` 字段注入，写起来最省事，但**不推荐**，因为：

- 依赖是"隐藏"的，看类定义看不出它需要哪些依赖
- 不方便测试（得靠反射注入）
- 容易形成循环依赖

**结论：优先用构造器注入。**

## Spring 里的 DI

Spring 容器本质上就是一个"超级工厂 + 依赖注入器"：

1. 你告诉 Spring"有哪些 Bean"（`@Component`、`@Bean`）
2. Spring 负责创建这些 Bean
3. Spring 负责把 Bean 之间的依赖自动注入（`@Autowired`）

你只管声明依赖，创建和装配的脏活累活，全交给容器。

这就是为什么用 Spring 之后，你几乎不用自己 `new` 对象了。

## DI 到底带来了什么

1. **解耦**：类只依赖抽象，不依赖具体实现
2. **可测试**：测试时注入 Mock 对象即可，不用连真数据库
3. **可替换**：换实现只需改配置，不用改代码
4. **集中管理**：对象的生命周期、作用域统一由容器管理

## 一个容易混淆的点

很多人分不清"DIP"和"IoC"和"DI"这三个词：

- **DIP（依赖倒置原则）**：是一个**设计原则**——"依赖抽象，不依赖细节"
- **IoC（控制反转）**：是一个**思想**——"创建对象的控制权反转给容器"
- **DI（依赖注入）**：是**实现 IoC 的具体手段**——通过构造器/Setter 注入依赖

简单记：**DIP 是原则，IoC 是思想，DI 是手段。**

## 写在最后

依赖注入这个模式，是理解 Spring、理解现代后端框架绕不开的一环。

理解了它，你才会明白为什么 Spring 能让你"面向接口编程"这件事变得如此自然。

下一篇回到数据结构，聊一个比树更复杂、但也更强大的结构——图。
