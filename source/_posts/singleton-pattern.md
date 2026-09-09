---
title: 单例模式：饿汉、懒汉、双重检查锁，到底怎么选
categories:
  - 基础
tags:
  - 设计模式
  - 单例模式
  - Java
description: 单例是面试和代码里出现频率最高的设计模式。饿汉、懒汉、双重检查锁、枚举，这几种写法的差别和坑，一次说清楚。
date: 2026-01-05 10:00:00
---

单例模式大概是每个学 Java 的人第一个接触的设计模式，也是面试里被问烂、但很多人其实没真懂的一个。

它的目标很简单：**保证一个类在整个系统中只有一个实例，并提供一个全局访问点**。

为什么需要单例？典型场景：配置管理、线程池、数据库连接池、日志器、Spring 容器里的 Bean（默认就是单例）。这些对象如果重复创建，要么浪费资源，要么状态不一致。

难的不是"理解目标"，是**在并发下正确、安全地实现它**。

## 写法一：饿汉式

```java
public class Singleton {
    private static final Singleton INSTANCE = new Singleton();

    private Singleton() {}

    public static Singleton getInstance() {
        return INSTANCE;
    }
}
```

类加载的时候就创建实例，所以叫"饿汉"——不管用不用，先造出来。

- 优点：简单，线程安全（由 JVM 类加载机制保证）
- 缺点：如果这个对象创建代价大，但你根本没用它，就浪费了

## 写法二：懒汉式（有 bug 的版本）

```java
public class Singleton {
    private static Singleton instance;

    private Singleton() {}

    public static Singleton getInstance() {
        if (instance == null) {
            instance = new Singleton();
        }
        return instance;
    }
}
```

"懒汉"——用到的时候才创建。但这段代码在单线程下没问题，多线程下会出 bug。

两个线程同时判断 `instance == null` 都为 true，就会创建出两个实例。单例就失效了。

## 写法三：双重检查锁（DCL）

```java
public class Singleton {
    private static volatile Singleton instance;

    private Singleton() {}

    public static Singleton getInstance() {
        if (instance == null) {              // 第一次检查
            synchronized (Singleton.class) {
                if (instance == null) {      // 第二次检查
                    instance = new Singleton();
                }
            }
        }
        return instance;
    }
}
```

两个 `if` 就是"双重检查"。为什么外面还要加一个 `synchronized`？因为同步锁开销大，不能每次调用都进锁，先用一次非同步的检查挡掉大部分情况，只有真正需要创建时才进锁。

这里有个**关键细节**：`instance` 为什么要用 `volatile` 修饰？

因为 `new Singleton()` 这个操作在 JVM 里不是原子的，它分三步：

1. 分配内存
2. 初始化对象
3. 把引用指向内存地址

指令重排序可能让第 3 步先于第 2 步执行。这样别的线程在第 1 次检查时，看到 `instance` 不为 null，但对象其实还没初始化完，拿到的就是一个"半成品"。`volatile` 禁止了这种重排序，保证拿到的一定是完整的对象。

**这个细节是面试高频考点**，很多人只会背 DCL 的代码，却说不清 `volatile` 是干嘛的。

## 写法四：枚举（推荐）

```java
public enum Singleton {
    INSTANCE;

    public void doSomething() {
        // ...
    }
}
```

这是《Effective Java》作者 Joshua Bloch 推荐的写法。

- 写法最简单
- 由 JVM 保证线程安全
- 还能防止反序列化和反射破坏单例

唯一的"缺点"是它不是懒加载的，但绝大多数场景下这不是问题。

**如果让我在生产代码里选，我会直接用枚举**——简单、安全、不易出错。

## 两个容易忽略的坑

### 1. 反射可以破坏单例

即使构造函数是 `private`，反射也能暴力调用它：

```java
Constructor<Singleton> c = Singleton.class.getDeclaredConstructor();
c.setAccessible(true);
Singleton s2 = c.newInstance();
```

枚举单例天然免疫这个问题，因为 JVM 禁止通过反射创建枚举实例。

### 2. 序列化会破坏单例

反序列化时，Java 会调用 `readResolve()` 重新生成一个对象。如果想让单例在序列化后仍然是同一个实例，需要：

```java
private Object readResolve() {
    return INSTANCE;
}
```

枚举同样自动处理了这个问题。

## 小结

| 写法 | 线程安全 | 懒加载 | 反序列化/反射安全 | 推荐度 |
|------|---------|--------|------------------|--------|
| 饿汉 | ✅ | ❌ | ❌ | 中 |
| 懒汉 | ❌ | ✅ | ❌ | 低 |
| DCL | ✅ | ✅ | ❌ | 中 |
| 枚举 | ✅ | ❌ | ✅ | 高 |

结论很简单：**能用枚举就用枚举，不能用再考虑 DCL**。

单例虽小，但它把"并发安全"、"指令重排序"、"序列化"这几个 Java 底层的坑都串起来了。搞懂单例，其实是搞懂了一串 Java 基础。
