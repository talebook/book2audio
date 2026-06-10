"""说话人识别 L1 规则层原型 — 在 chat.txt 上验证规则覆盖率

规则（按优先级）：
  R1 引号后随附：“...”X<动作/说话动词>   （同段，引号紧跟名字）
  R2 引号前导：X<说话动词>[:：]“...”      （同段，名字+动词在引号前）
  R3 邻段主语：引号独立成段时，看下一段/上一段旁白的开头主语
  R4 两人对话轮替：连续无线索对白，按最近两个说话人交替
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from book2audio.parser import QUOTE_RE  # noqa: E402

SPEECH_VERBS = "说|道|笑|喊|叫|骂|问|答|哭|嚷|吼|呵斥|嘀咕|低语|感叹|叹|回|应"
NAME = r"[一-龥]{2,3}"

# 名字 + （修饰语）+ 说话/动作动词
R1_AFTER = re.compile(rf"^({NAME})[^“”]{{0,8}}?(?:{SPEECH_VERBS})")
R2_BEFORE = re.compile(rf"({NAME})[^“”]{{0,12}}?(?:{SPEECH_VERBS})[^“”]{{0,4}}[:：]?\s*$")
SUBJ_LEAD = re.compile(rf"^({NAME})")


def build_name_list(text: str) -> set:
    """从全文统计 紧邻说话动词的候选人名，2/3字候选都计数（避免贪婪误吞），出现>=2次的认为是角色名。"""
    counts = {}
    for n_len in (2, 3):
        for m in re.finditer(rf"(?=([一-龥]{{{n_len}}})(?:{SPEECH_VERBS}))", text):
            n = m.group(1)
            counts[n] = counts.get(n, 0) + 1
    # 同时统计段首主语（2字与3字前缀都计）
    for para in text.splitlines():
        para = para.strip()
        for n_len in (2, 3):
            m = re.match(rf"([一-龥]{{{n_len}}})", para)
            if m:
                counts[m.group(1)] = counts.get(m.group(1), 0) + 1
    # 去掉作为更长名字前缀的短候选（"李项"⊂"李项平"）
    names = {n for n, c in counts.items() if c >= 2}
    return {n for n in names if not any(o != n and o.startswith(n) and counts[o] >= counts[n] for o in names)}


def known(names: set, cand: str):
    """候选串匹配到已知角色名（含后缀截断，如'李项平哈'→'李项平'）。"""
    for n in sorted(names, key=len, reverse=True):
        if cand.startswith(n) or n.startswith(cand):
            return n
    return None


def attribute(text: str):
    names = build_name_list(text)
    paras = [p.strip() for p in text.splitlines() if p.strip()]
    results = []  # (quote, speaker, rule)
    recent = []   # 轮替用的最近说话人

    for idx, para in enumerate(paras):
        quotes = list(QUOTE_RE.finditer(para))
        if not quotes:
            continue
        for qi, q in enumerate(quotes):
            speaker, rule = None, None
            after = para[q.end():]
            before = para[:q.start()]

            # R1: 引号后紧跟 名字+动词
            m = re.match(rf"\s*({NAME})", after)
            if m and known(names, m.group(1)) and re.match(rf"\s*{NAME}[^“”]{{0,8}}?(?:{SPEECH_VERBS})", after):
                speaker, rule = known(names, m.group(1)), "R1后随"
            # R2: 引号前 名字+动词
            if not speaker:
                m = R2_BEFORE.search(before)
                if m and known(names, m.group(1)):
                    speaker, rule = known(names, m.group(1)), "R2前导"
            # R3: 引号独立成段 → 邻段旁白主语
            if not speaker and not before.strip() and not after.strip():
                for j in (idx + 1, idx - 1):
                    if 0 <= j < len(paras) and not QUOTE_RE.search(paras[j]):
                        m = SUBJ_LEAD.match(paras[j])
                        if m and known(names, m.group(1)):
                            speaker, rule = known(names, m.group(1)), f"R3邻段({'下' if j > idx else '上'})"
                            break
            # 同段多引号：归属同一说话人
            if not speaker and qi > 0 and results and results[-1][1]:
                speaker, rule = results[-1][1], "同段沿用"
            # R4: 两人轮替
            if not speaker and len(set(recent[-2:])) == 2:
                last_two = recent[-2:]
                speaker, rule = (last_two[0] if last_two[1] == recent[-1] else last_two[1]), "R4轮替?"
                speaker = last_two[0]  # 与最近一个不同的那位
                rule = "R4轮替?"

            results.append((q.group(1), speaker, rule))
            if speaker:
                recent.append(speaker)
    return names, results


if __name__ == "__main__":
    text = Path(sys.argv[1] if len(sys.argv) > 1 else "book/chat.txt").read_text(encoding="utf-8")
    names, results = attribute(text)
    print(f"自动识别的角色名: {sorted(names)}\n")
    ok = 0
    for quote, speaker, rule in results:
        mark = speaker or "❓未识别"
        print(f"  [{rule or '--':-^10}] {mark:　<5} ←  “{quote[:25]}”")
        ok += bool(speaker)
    print(f"\n规则层归属率: {ok}/{len(results)} = {ok/len(results):.0%}")
