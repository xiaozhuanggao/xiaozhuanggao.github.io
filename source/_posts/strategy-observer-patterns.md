---
title: 策略模式与观察者模式：从 if-else 地狱里爬出来
categories:
  - 基础
tags:
  - 设计模式
  - 策略模式
  - 观察者模式
  - 行为型
description: 策略模式帮你消灭又长又臭的 if-else，观察者模式帮你解耦事件的通知者和处理者。这是两个最常用、最能立竿见影的行为型模式。
date: 2026-01-09 10:00:00
---

如果说创建型模式解决的是"怎么 new 对象"，那行为型模式解决的就是"对象之间怎么协作"。

策略模式和观察者模式，是行为型模式里最常用、也最能立刻改善你代码质量的两个。

## 策略模式：消灭 if-else 地狱

先看一段真实的坏代码。假设你在写电商的优惠券系统，有满减、折扣、立减三种优惠：

```java
public double calcPrice(String type, double price) {
    if ("fullReduction".equals(type)) {
        return price - 100;
    } else if ("discount".equals(type)) {
        return price * 0.8;
    } else if ("directReduction".equals(type)) {
        return price - 30;
    } else {
        return price;
    }
}
```

这段代码的问题：

1. **分支会越来越多**——以后加"满 300 减 50"，就得再改这个方法
2. **每个分支的逻辑会长大**——真实的优惠计算远不止一行
3. **无法独立测试**——要测一个分支，得把整个方法跑一遍

策略模式的解法：**把每种算法封装成一个独立的类，让它们可以互相替换**。

```java
public interface PricingStrategy {
    double calc(double price);
}

public class FullReductionStrategy implements PricingStrategy {
    public double calc(double price) { return price - 100; }
}

public class DiscountStrategy implements PricingStrategy {
    public double calc(double price) { return price * 0.8; }
}
```

使用时：

```java
PricingStrategy strategy = strategyMap.get(type);
double result = strategy.calc(price);
```

新增一种优惠，就是新增一个类，**完全不用碰已有代码**。这就是开闭原则的体现。

### 策略模式的心法

判断一段 if-else 要不要用策略模式，看两个信号：

1. **分支会持续增加**
2. **每个分支的逻辑比较复杂，会各自演化**

如果只是两三个简单分支、未来也不会变，那 if-else 反而更直观，别过度设计。

## 观察者模式：解耦"通知"和"处理"

观察者模式你可能天天在用，只是没意识到——它就是**发布-订阅**。

场景：用户下单成功后，要做一系列事情：发短信、扣库存、发优惠券、记日志。

最朴素的写法是在下单方法里把这些事全写进去。但这样下单逻辑就和这些"副作用"耦合死了，加一个动作就得改下单代码。

观察者模式的解法：**下单只负责"发通知"，谁关心这个通知，谁自己来订阅**。

```java
public interface OrderListener {
    void onOrderCreated(Order order);
}

public class OrderService {
    private List<OrderListener> listeners = new ArrayList<>();

    public void addListener(OrderListener l) { listeners.add(l); }

    public void createOrder(Order order) {
        // 核心下单逻辑
        for (OrderListener l : listeners) {
            l.onOrderCreated(order);
        }
    }
}
```

发短信、扣库存、发优惠券，各自实现成一个 `OrderListener` 注册进来。要加一个新动作，注册一个新的 Listener 就行。

### 观察者模式的价值

- **解耦**：被观察者（OrderService）不知道、也不关心有哪些观察者
- **可扩展**：新增观察者不影响已有代码
- **现实映射**：消息队列、事件驱动、RxJava、Vue 的响应式，底层都是这个思路

Spring 里的 `ApplicationEvent` + `@EventListener`，就是这个模式的框架级实现。

## 两个模式放在一起看

| 模式 | 解决什么问题 | 核心思想 |
|------|-------------|---------|
| 策略模式 | 多种算法可以替换 | 把算法封装成对象 |
| 观察者模式 | 事件通知与处理解耦 | 一方发布，多方订阅 |

它们都在做同一件事：**把"变化的部分"抽出来，隔离掉**。

策略模式抽离的是"变化的算法"，观察者模式抽离的是"变化的处理者"。

## 写在最后

学设计模式，我最大的体会是：**模式之间是相通的**。

策略模式和观察者模式，本质上都是在用"多态"来应对"变化"。理解了这一点，你就不是在背模式，而是在理解面向对象的核心思想。

下一篇，我们离开设计模式，回到更底层的东西——数据结构。
