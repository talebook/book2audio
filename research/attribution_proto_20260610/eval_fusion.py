"""评估 src/book2audio/attribution.py 的 L1+L2 融合效果

用法: uv run python research/attribution_proto_20260610/eval_fusion.py [--no-csi]
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from book2audio.attribution import Attributor  # noqa: E402


def main():
    use_csi = "--no-csi" not in sys.argv
    text = (ROOT / "book/chat.txt").read_text(encoding="utf-8")
    gold = [q["speaker"] for q in json.loads(
        (Path(__file__).parent / "gold_chat.json").read_text())["quotes"]]

    att = Attributor(csi_model_dir=ROOT / "models/csi-v1" if use_csi else None)
    quotes = att.attribute(text)
    assert len(quotes) == len(gold), f"引文数不一致 {len(quotes)} vs {len(gold)}"

    correct = 0
    for q, g in zip(quotes, gold):
        ok = q.speaker == g
        correct += ok
        print(f"  {'✅' if ok else '❌'} [{q.method:>4}] 预测={q.speaker or '∅':　<5} 金标={g:　<4} “{q.text[:20]}”")
    mode = "L1+L2融合" if use_csi else "仅L1规则"
    print(f"\n{mode} 准确率: {correct}/{len(gold)} = {correct/len(gold):.0%}")


if __name__ == "__main__":
    main()
