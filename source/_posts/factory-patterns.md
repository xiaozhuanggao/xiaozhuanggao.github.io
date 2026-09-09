---
title: 工厂方法与抽象工厂：别再混为一谈
categories:
  - 基础
tags:
  - 设计模式
  - 工厂模式
  - 创建型
description: 简单工厂、工厂方法、抽象工厂是三个名字很像、却解决不同问题的模式。这篇文章把它们的关系和演进逻辑一次讲清楚。
date: 2026-01-07 10:00:00
---

面试里经常出现这样的对话：

> "讲讲工厂模式。"
> "工厂模式有简单工厂、工厂方法、抽象工厂……"

然后就开始背定义。但背完往往自己也是糊的，因为这三个名字实在太像了。

其实它们的演进逻辑非常清晰，理清了就永远忘不掉。

## 起点：到处 new 的坏味道

假设你在做一个支付系统，支持微信和支付宝两种支付方式。最初你可能会这么写：

```java
if ("wechat".equals(type)) {
    return new WeChatPay();
} else if ("alipay".equals(type)) {
    return new AliPay();
}
```

问题来了：如果以后要加"银联支付"、"苹果支付"，这段 if-else 就得一直改，而且这样的判断散落在代码各处，改一处漏一处。

**创建对象的逻辑，不应该和业务逻辑混在一起**。这就是工厂模式要解决的问题。

## 第一站：简单工厂

把创建逻辑抽到一个"工厂"里：

```java
public class PayFactory {
    public static Pay create(String type) {
        switch (type) {
            case "wechat": return new WeChatPay();
            case "alipay": return new AliPay();
            default: throw new IllegalArgumentException();
        }
    }
}
```

调用方不再关心具体创建哪个类，只要告诉工厂"我要哪种"。

简单工厂**不是 GoF 的 23 种模式之一**，它更像一个"编程习惯"。它的缺点也很明显：新增支付方式时，还是要改工厂里的 switch，违反开闭原则。

## 第二站：工厂方法

工厂方法的思路是：**把"创建哪个类"的决定，推迟到子类去**。

```java
public interface PayFactory {
    Pay create();
}

public class WeChatPayFactory implements PayFactory {
    public Pay create() { return new WeChatPay(); }
}

public class AliPayFactory implements PayFactory {
    public Pay create() { return new AliPay(); }
}
```

现在要加"银联支付"，只需要新增一个 `UnionPayFactory` 类，**不需要改动任何现有代码**——这就符合开闭原则了。

工厂方法的核心：**一个工厂，创建一种产品**。产品有多态，工厂也有多态。

## 第三站：抽象工厂

工厂方法解决的是"一种产品"的创建。但现实中经常是"一组相关产品"。

比如一套 UI 组件，有 Button 和 TextField。Windows 风格和 Mac 风格各是一套，而且它们必须配套使用——你不能用 Windows 的 Button 配 Mac 的 TextField。

抽象工厂解决的就是这个问题：**一个工厂，创建一族相关产品**。

```java
public interface UIFactory {
    Button createButton();
    TextField createTextField();
}

public class WindowsUIFactory implements UIFactory { ... }
public class MacUIFactory implements UIFactory { ... }
```

这样拿到一个 `WindowsUIFactory`，创建出来的 Button 和 TextField 一定是配套的 Windows 风格。

## 一张表理清区别

| 模式 | 解决什么 | 关键点 |
|------|---------|--------|
| 简单工厂 | 集中创建逻辑 | 一个工厂 + switch |
| 工厂方法 | 一种产品的多态创建 | 每个产品一个工厂类 |
| 抽象工厂 | 一族相关产品的创建 | 一个工厂创建多个配套产品 |

**它们的共同点**：都把"对象的创建"和"对象的使用"解耦了，让代码面对"新增产品"时更从容。

## 现实中的使用

说实话，在 Spring 时代，我们很少手写工厂了。

因为 Spring 容器本身就是个超级工厂，`@Bean`、`@Autowired` 已经在替我们管理对象的创建。但理解工厂模式的思路依然重要，因为：

- Spring 的 `FactoryBean` 就是工厂方法的变体
- 很多框架的 SPI 机制本质是抽象工厂
- 理解了"创建与使用解耦"，才能理解依赖注入（后面会专门讲）

所以别再死记三个名词了。记住这条线就够了：

> **简单工厂是习惯，工厂方法是"一种产品"，抽象工厂是"一族产品"。**
