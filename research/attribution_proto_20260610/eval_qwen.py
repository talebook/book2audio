"""Qwen(ollama) vs CSI 说话人识别对比评测：同上下文窗口、同金标

用法: uv run python research/attribution_proto_20260610/eval_qwen.py [model]
      model 默认 qwen3:0.6b，可传 qwen3.5:0.8b
"""

import json
import re
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "research/attribution_proto_20260610"))
from proto_csi import build_sample, split_units  # noqa: E402  复用同样的上下文构造

OLLAMA = "http://localhost:11434/api/generate"

PROMPT = """阅读下面的小说片段，判断引文「{quote}」是谁说的。

片段：
{context}

只输出说话人的名字（2-4个字），不要解释。如果无法判断，输出：未知"""


def ask(model: str, prompt: str) -> tuple:
    body = json.dumps({"model": model, "prompt": prompt, "stream": False, "think": False,
                       "options": {"temperature": 0, "num_predict": 24}}).encode()
    t0 = time.time()
    req = urllib.request.Request(OLLAMA, body, {"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        resp = json.loads(r.read())["response"]
    # 清掉可能的思考标签与标点
    resp = re.sub(r"<think>.*?</think>", "", resp, flags=re.S)
    resp = resp.strip().strip("。！？：:\"“”「」")
    return resp, time.time() - t0


def main():
    model = sys.argv[1] if len(sys.argv) > 1 else "qwen3:0.6b"
    text = (ROOT / "book/chat.txt").read_text(encoding="utf-8")
    gold = [q["speaker"] for q in json.loads(
        (Path(__file__).parent / "gold_chat.json").read_text())["quotes"]]

    units = split_units(text)
    qis = [i for i, u in enumerate(units) if u[1]]
    assert len(qis) == len(gold)

    correct, times = 0, []
    for n, qi in enumerate(qis):
        _, context = build_sample(units, qi)   # 与CSI相同的 前3句+引文+后3句
        quote = units[qi][0][1:-1]
        ans, dt = ask(model, PROMPT.format(quote=quote[:50], context=context))
        times.append(dt)
        g = gold[n]
        ok = bool(ans) and (g in ans or ans in g)
        correct += ok
        print(f"  {'✅' if ok else '❌'} 预测={ans[:12]:　<7} 金标={g:　<4} {dt:.1f}s “{quote[:18]}”")
    print(f"\n{model}: 准确率 {correct}/{len(gold)} = {correct/len(gold):.0%}，单条平均 {sum(times)/len(times):.1f}s")


if __name__ == "__main__":
    main()
