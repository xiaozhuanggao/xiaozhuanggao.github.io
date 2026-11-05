#!/usr/bin/env python3
"""从 public/sitemap.xml 抽取最近的站内文章 URL，写入 baidu_urls.txt 供百度主动推送。

不在此文件里写任何密钥；token 由 GitHub Actions secret 在运行时注入。
"""
import xml.etree.ElementTree as ET
import sys

SITEMAP = "public/sitemap.xml"
OUT = "baidu_urls.txt"
SITE = "https://gaoxiaozhuang.me/"
NS = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
LIMIT = 50  # 单批上限，配合百度每日配额；新文一定在最前，必被覆盖


def main():
    urls = []
    try:
        tree = ET.parse(SITEMAP)
        root = tree.getroot()
        for u in root.findall("s:url", NS):
            loc = u.find("s:loc", NS)
            lm = u.find("s:lastmod", NS)
            if loc is not None and loc.text:
                urls.append((lm.text if (lm is not None and lm.text) else "", loc.text))
    except Exception as e:
        print("sitemap parse failed:", e, file=sys.stderr)

    # 首页始终纳入，并排在最前优先级
    urls.append(("9999", SITE))
    # 按 lastmod 倒序：最新的文章永远先被推送，确保新稿优先进入配额
    urls.sort(key=lambda x: x[0], reverse=True)
    top = [u[1] for u in urls[:LIMIT]]
    with open(OUT, "w") as f:
        f.write("\n".join(top) + "\n")
    print(f"wrote {len(top)} urls to {OUT}")


if __name__ == "__main__":
    main()
