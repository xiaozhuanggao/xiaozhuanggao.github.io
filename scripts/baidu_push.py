#!/usr/bin/env python3
"""百度主动推送（带跨次运行状态的轮转脚本）。

设计目标：
- 百度给新站主动推送额度约 10 条/天，超额部分静默丢弃。
- 因此不能一次把全站 POST 过去，而是要「每天推 10 条、按最旧→最新轮转」，
  用 artifact 存进度，约 8 天把旧文扫完，之后新文继续接上。
- 每天先纳入「近 2 天内、尚未推送」的新文（保证新稿不丢），
  再用剩余额度从 cursor 继续往下扫最旧的未推送文章。

不在此文件里写任何密钥；site / token 由调用方（GitHub Actions）注入。
"""
import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta

NS = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
FRESH_WINDOW_DAYS = 2  # 近 N 天内发布的文章，无论轮转进度都优先推送


def _parse_dt(text):
    """把 sitemap 的 lastmod 转成 epoch 秒；无法解析则视为最旧。"""
    if not text:
        return 0.0
    try:
        t = text.strip()
        if t.endswith("Z"):
            t = t[:-1] + "+00:00"
        dt = datetime.fromisoformat(t)
        if dt.tzinfo is not None:
            dt = dt.astimezone()  # 转本地时区以便与 now() 比较
        return dt.timestamp()
    except Exception:
        return 0.0


def parse_sitemap(path):
    out = []
    try:
        root = ET.parse(path).getroot()
    except Exception as e:
        print(f"[warn] 无法解析 sitemap: {e}", file=sys.stderr)
        return out
    for u in root.findall(f"{NS}url"):
        loc = u.find(f"{NS}loc")
        if loc is None or not loc.text:
            continue
        lm = u.find(f"{NS}lastmod")
        out.append((loc.text.strip(), _parse_dt(lm.text if lm is not None else "")))
    return out


def build_sequence(urls, site):
    """首页恒在前，其余按发表日期升序（最旧→最新），保证轮转从最旧开始扫。

    排序键优先取 URL 路径里的 /YYYY/MM/DD/（最可靠），取不到再用 lastmod。
    """
    homepage = site.rstrip("/") + "/"
    url_date = re.compile(r"/(\d{4})/(\d{2})/(\d{2})/")

    def sort_key(item):
        u, ts = item
        m = url_date.search(u)
        if m:
            y, mo, d = (int(x) for x in m.groups())
            return y * 10000 + mo * 100 + d
        return 0  # 没有日期的（理论上已被过滤掉）排最前

    rest = sorted([(u, ts) for u, ts in urls if u != homepage], key=sort_key)
    seq = [homepage] + [u for u, _ in rest]
    return seq


def load_state(path):
    if not path or not os.path.exists(path):
        return {"pushed": [], "cursor": 0}
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            raise ValueError("bad state")
        data.setdefault("pushed", [])
        data.setdefault("cursor", 0)
        return data
    except Exception as e:
        print(f"[warn] 读取状态失败，视为空: {e}", file=sys.stderr)
        return {"pushed": [], "cursor": 0}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sitemap", required=True)
    ap.add_argument("--state", required=True)
    ap.add_argument("--site", required=True)
    ap.add_argument("--token", required=True)
    ap.add_argument("--quota", type=int, default=10)
    ap.add_argument("--api", default="http://data.zz.baidu.com/urls")
    args = ap.parse_args()

    urls = parse_sitemap(args.sitemap)
    if not urls:
        print("[skip] sitemap 为空或无法解析，本次不推送")
        return

    # 只推「首页 + 带日期的文章」，跳过标签/分类/归档等系统页，
    # 避免 10 条/天的额度被稀释（334 条里 257 条是系统页）。
    homepage = args.site.rstrip("/") + "/"
    dated = re.compile(r"/\d{4}/\d{2}/\d{2}/")
    urls = [(u, ts) for u, ts in urls if u == homepage or dated.search(u)]
    if not urls:
        print("[skip] 过滤后无文章 URL，本次不推送")
        return

    seq = build_sequence(urls, args.site)
    n = len(seq)
    state = load_state(args.state)
    pushed = set(state.get("pushed", []))
    cursor = int(state.get("cursor", 0)) % max(1, n)

    now = datetime.now().timestamp()
    fresh_cutoff = now - FRESH_WINDOW_DAYS * 86400

    # 1) 近 2 天内的新文优先
    batch = []
    for u in seq:
        if u in pushed:
            continue
        ts = 0.0
        # 重新取 lastmod：seq 只存 url，需回查
        # 简化：用 url 在 urls 里的映射
        pass
    # 建立 url->ts 映射，供新鲜度判断
    ts_map = {u: ts for u, ts in urls}
    for u in seq:
        if u in pushed:
            continue
        if ts_map.get(u, 0) >= fresh_cutoff:
            batch.append(u)
            if len(batch) >= args.quota:
                break

    # 2) 用剩余额度从 cursor 继续轮转（最旧→最新）
    remaining = args.quota - len(batch)
    if remaining > 0:
        idx = cursor
        added = 0
        for _ in range(n):
            cand = seq[idx % n]
            idx = (idx + 1) % n
            if cand in pushed or cand in batch:
                continue
            batch.append(cand)
            added += 1
            if added >= remaining:
                break
        cursor = idx  # 下次从这儿继续

    if not batch:
        print("[skip] 没有需要推送的 URL（存量已扫完、且无新文）")
        state["pushed"] = sorted(pushed)
        state["cursor"] = cursor
        _save_state(args.state, state)
        return

    payload = "\n".join(batch)
    api = f"{args.api}?site={args.site.rstrip('/')}&token={args.token}"
    req = urllib.request.Request(
        api, data=payload.encode("utf-8"), headers={"Content-Type": "text/plain"}
    )
    try:
        with urllib.request.urlopen(req, timeout=25) as resp:
            body = resp.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        print(f"[error] HTTP {e.code}: {e.read().decode('utf-8', 'replace')}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"[error] 请求失败: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"[baidu] {body}")

    # 百度按提交顺序处理前 success 条；仅标记成功的部分为已推送
    success = 0
    try:
        success = int(json.loads(body).get("success", 0))
    except Exception:
        success = len(batch)
    accepted = batch[: max(0, success)]
    for u in accepted:
        pushed.add(u)

    # cursor 推进到「最后一条被接受的文章」之后，未接受的尾巴下一轮会再扫到
    if accepted:
        last = accepted[-1]
        try:
            cursor = (seq.index(last) + 1) % n
        except ValueError:
            pass

    state["pushed"] = sorted(pushed)
    state["cursor"] = cursor
    _save_state(args.state, state)

    print(
        f"[summary] 本次提交 {len(batch)} 条，百度受理 {success} 条；"
        f"累计已推送 {len(pushed)}/{n} 条；下一轮 cursor={cursor}"
    )


def _save_state(path, state):
    try:
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[warn] 保存状态失败: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
