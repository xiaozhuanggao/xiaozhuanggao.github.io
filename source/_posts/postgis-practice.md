---
title: PostgreSQL + PostGIS 地理数据实践
categories:
  - Database
  - PostGIS
tags:
  - PostGIS
  - PostgreSQL
  - GIS
description: 从空间数据类型到常见查询，梳理 PostGIS 处理地理数据的核心用法与性能要点。
date: 2026-04-16 10:00:00
---

# PostgreSQL + PostGIS 地理数据实践

> 当业务里出现"点、线、面、轨迹、空间关系"这些概念时，PostGIS 是 PostgreSQL 最有力的扩展。本文梳理它的核心用法。

## 为什么不用 MySQL 存地理数据

MySQL 也有空间类型，但能力远弱于 PostGIS。PostGIS 提供：

- 完整的几何类型（点、线、面、多点、集合）
- 丰富的空间函数（距离、包含、相交、缓冲区）
- 空间索引（GiST），让空间查询走索引

对 GIS 相关业务，PostgreSQL + PostGIS 是事实上的标准组合。

## 核心数据类型

```sql
-- 点
SELECT ST_GeomFromText('POINT(121.4737 31.2304)', 4326);

-- 线（轨迹）
SELECT ST_GeomFromText('LINESTRING(121.47 31.23, 121.48 31.24)', 4326);

-- 面（区域）
SELECT ST_GeomFromText('POLYGON((0 0, 1 0, 1 1, 0 1, 0 0))', 4326);
```

`4326` 是 WGS84 坐标系（GPS 经纬度）。国内业务如果涉及投影、测距，还需要理解 3857（Web 墨卡托）等投影坐标系的换算。

## 常用空间查询

```sql
-- 两个点之间的球面距离（米）
SELECT ST_Distance(
  ST_GeomFromText('POINT(121.47 31.23)', 4326)::geography,
  ST_GeomFromText('POINT(121.48 31.24)', 4326)::geography
);

-- 判断点是否在某区域内
SELECT ST_Contains(region, point) FROM areas;

-- 找某个点半径 500 米内的设施
SELECT name FROM facilities
WHERE ST_DWithin(
  geom, ST_GeomFromText('POINT(121.47 31.23)', 4326)::geography, 500
);
```

注意：涉及距离计算时用 `::geography` 类型，它会做球面计算；纯平面几何用 `geometry`。

## 空间索引是关键

空间查询不建索引会全表扫描，数据一大就是灾难：

```sql
CREATE INDEX idx_geom ON facilities USING GIST (geom);
```

只有建立了 GiST 索引，`ST_DWithin`、`ST_Contains` 这些函数才能真正走索引。

## 小结

PostGIS 上手不难，难的是理解**坐标系**和**索引**这两个概念。坐标系搞不清，距离算出来就是错的；索引不建，查询性能就是灾难。这两点理解了，PostGIS 就能真正为 GIS 业务所用。
