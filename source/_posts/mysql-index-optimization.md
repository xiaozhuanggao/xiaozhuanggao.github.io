---
title: MySQL 索引优化实战
categories:
  - Database
  - MySQL
tags:
  - MySQL
  - 索引
  - 性能优化
description: 系统讲解 MySQL 索引原理、常见失效场景与优化技巧。
abbrlink: 78f57cef
date: 2026-03-19 10:00:00
---

# MySQL 索引优化实战

> 索引是 MySQL 性能优化的第一抓手。本文系统梳理索引原理与实战经验。

## 索引基础

### B+ Tree 索引

InnoDB 默认索引结构是 B+ Tree：

- 叶子节点存储数据（聚簇索引）或主键（二级索引）
- 非叶子节点只存储键值和指针
- 叶子节点之间通过链表相连，适合范围查询

### 聚簇索引 vs 二级索引

- **聚簇索引**：叶子节点存完整行数据（每张表只有一个）
- **二级索引**：叶子节点存主键值，需要回表查询

## 索引失效的常见情况

| SQL 写法 | 是否走索引 |
|---------|-----------|
| `WHERE col + 1 = 5` | ❌ 函数失效 |
| `WHERE col LIKE '%abc'` | ❌ 前导模糊 |
| `WHERE col IS NULL` | ⚠️ 取决于数据分布 |
| `WHERE col IN (...)` | ✅ 命中索引 |
| `WHERE col = 'a' AND col2 = 'b'` | ✅ 联合索引 |

## 索引设计原则

1. **高频查询字段建索引**
2. **区分度高的字段建索引**（如 user_id，避免在 gender 上建索引）
3. **联合索引注意顺序**：最左前缀原则
4. **不要过度索引**：写入性能下降，占用空间

## EXPLAIN 解读

```sql
EXPLAIN SELECT * FROM users WHERE name = 'test' AND age > 18;
```

关键字段：

- **type**：ALL（全表扫描）→ index → range → ref → const
- **key**：实际使用的索引
- **rows**：扫描行数（越少越好）
- **Extra**：Using filesort / Using temporary 是性能警告

## 总结

索引不是越多越好。理解原理 + 配合 EXPLAIN 才能写出高效的 SQL。本站后续会持续更新 MySQL 优化实战。