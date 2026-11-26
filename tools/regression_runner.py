#!/usr/bin/env python3
"""
regression_runner.py — D 原话回归测试 runner（understanding-d 验收锚点）

用法:
    python3 regression_runner.py [--temp 0.3] [--max-tokens 800] [--tag v1]

流程: 读 regression-test-set-v0.md 场景 → A 裸答 / B persona 注入 → 存 JSON。
打分是 Lead 语义判断（本脚本不打分），输出 JSON 供逐条对照。
persona 注入 = persona-map-skeleton.md 的 §1 认知层 + §4 taste + §5 盲区。

历史: v0 首轮 2026-11-26: A 25% / B 75% 严格一致率 (n=12, Lead 打分)。
"""
import argparse, json, re, sys, time, urllib.request, pathlib

WS = pathlib.Path("/Users/a1-6/Desktop/workspace")
UD = WS / "projects/AI-计算科学/D1-persona-align/tasks/understanding-d"
API = "http://127.0.0.1:8787/v1/chat/completions"
MODEL = "qwen3.8-27b-mtp"


def load_scenes():
    text = (UD / "regression-test-set-v0.md").read_text()
    entries = re.findall(r"### (R\d+) ([^\n]*)\n(.*?)(?=\n### |\n## )", text, re.S)
    out = []
    for rid, title, body in entries:
        m_scene = re.search(r"- 场景：(.*?)(?=\n- )", body, re.S)
        m_gt = re.search(r"Ground truth：(.*?)(?=\n- )", body, re.S)
        if not m_scene or not m_gt:
            continue
        scene = m_scene.group(1).strip()
        gt = m_gt.group(1).strip()
        out.append({"id": rid, "title": title.strip(), "scene": scene, "gt": gt})
    return out


def persona_inject():
    md = (UD / "persona-map-skeleton.md").read_text()

    def section(s, e):
        m = re.search(s, md)
        if not m:
            return ""
        rest = md[m.start():]
        x = re.search(e, rest[10:])
        return rest[: x.start() + 10] if x else rest[:4000]

    return "\n\n".join([
        section(r"## 1\. ", r"## 2\. "),
        section(r"## 4\. ", r"## 5\. "),
        section(r"## 5\. ", r"## 6\. "),
    ])


def ask(prompt, temp, max_tokens):
    payload = json.dumps({
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temp, "max_tokens": max_tokens,
    }).encode()
    req = urllib.request.Request(API, data=payload,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=180) as r:
        return json.loads(r.read())["choices"][0]["message"]["content"].strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--temp", type=float, default=0.3)
    ap.add_argument("--max-tokens", type=int, default=800)
    ap.add_argument("--tag", default=time.strftime("%Y%m%d-%H%M%S"))
    args = ap.parse_args()

    scenes = load_scenes()
    pinj = persona_inject()
    print(f"scenes={len(scenes)} persona_inject={len(pinj)}chars tag={args.tag}")

    results = []
    for s in scenes:
        row = dict(s)
        row["A_baseline"] = ask(
            f"面对以下情境，你会做什么判断？简要回答（100字内）。\n\n情境：{s['scene']}",
            args.temp, 300)
        row["B_persona"] = ask(
            f"你是某研究者的数字分身。根据以下关于他的材料，面对情境时他最可能做什么判断？先推理，最后一行必须以『判断：』开头给出结论（30字内）。\n\n材料：\n{pinj}\n\n情境：{s['scene']}",
            args.temp, args.max_tokens)
        results.append(row)
        print(f"{row['id']} done ({time.strftime('%H:%M:%S')})")

    out = UD / f"regression-run-{args.tag}.json"
    out.write_text(json.dumps(results, ensure_ascii=False, indent=1))
    print(f"SAVED {out}")
    print("打分: Lead 语义判断（一致/部分/不一致），对照 gt 字段逐条评")


if __name__ == "__main__":
    main()
