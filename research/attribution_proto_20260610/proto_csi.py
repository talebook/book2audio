"""说话人识别 L2 原型：CSI 模型（chinese-roberta-wwm-ext-large-csi-v1，抽取式MRC）

输入构造（沿用 easytts/csi 的方案）：
  question = 引文 + 相邻的一句旁白（提供归属线索）
  context  = 前3句 + 引文 + 后3句
  模型从 context 中抽取说话人 span（start/end logits）

用法：
  uv run python research/attribution_proto_20260610/proto_csi.py book/chat.txt \
      research/attribution_proto_20260610/gold_chat.json
"""

import json
import re
import sys
from pathlib import Path

import torch
from tokenizers import BertWordPieceTokenizer
from transformers import BertConfig, BertForQuestionAnswering

MODEL_DIR = Path(__file__).resolve().parents[2] / "models/csi-v1"
QUOTE_RE = re.compile(r"[“「]([^”」]*)[”」]")
SENT_SPLIT = re.compile(r"(?<=[。！？\n])")


def load_model():
    # 注意：transformers 5.x 的 BertTokenizer(vocab_file=...) 裸构建会把中文全变 [UNK]，必须用 tokenizers 库
    tokenizer = BertWordPieceTokenizer(str(MODEL_DIR / "vocab.txt"), lowercase=True)
    tokenizer.enable_truncation(max_length=512, strategy="only_second")
    config = BertConfig.from_json_file(MODEL_DIR / "config.json")
    model = BertForQuestionAnswering(config)
    state = torch.load(MODEL_DIR / "csi-v1.pth", map_location="cpu", weights_only=True)
    missing, unexpected = model.load_state_dict(state, strict=False)
    # 仅允许位置编码缓冲区之类的差异，核心权重必须全部命中
    bad = [k for k in missing if "position_ids" not in k]
    bad_unexpected = [k for k in unexpected if "pooler" not in k]  # QA头不使用pooler
    if bad or bad_unexpected:
        raise RuntimeError(f"权重不匹配 missing={bad[:5]} unexpected={bad_unexpected[:5]}")
    model.eval()
    return tokenizer, model


def split_units(text: str):
    """切分为句子单元，引文整体作为一个单元。返回 [(text, is_quote)]"""
    units = []
    pos = 0
    for m in QUOTE_RE.finditer(text):
        for s in SENT_SPLIT.split(text[pos:m.start()]):
            if s.strip():
                units.append((s.strip(), False))
        units.append((m.group(0), True))
        pos = m.end()
    for s in SENT_SPLIT.split(text[pos:]):
        if s.strip():
            units.append((s.strip(), False))
    return units


def build_sample(units, qi, win=3):
    """按 easytts 方案为第 qi 个单元（引文）构造 (question, context)。"""
    quote = units[qi][0]
    pre = "".join(u[0] for u in units[max(0, qi - win):qi])
    post = "".join(u[0] for u in units[qi + 1:qi + 1 + win])
    # question = 引文 + 相邻旁白句（优先前句）
    if qi > 0 and not units[qi - 1][1]:
        question = units[qi - 1][0] + quote
    elif qi + 1 < len(units) and not units[qi + 1][1]:
        question = quote + units[qi + 1][0]
    else:
        question = quote
    context = f"{pre} {quote} {post}"
    return question, context


@torch.no_grad()
def predict_span(tokenizer, model, question: str, context: str, max_ans_len=10):
    enc = tokenizer.encode(question, context)
    input_ids = torch.tensor([enc.ids])
    type_ids = torch.tensor([enc.type_ids])
    attn = torch.tensor([enc.attention_mask])
    out = model(input_ids=input_ids, token_type_ids=type_ids, attention_mask=attn)
    offsets = enc.offsets
    is_ctx = torch.tensor([sid == 1 and enc.ids[i] not in (101, 102)  # 排除[CLS]/[SEP]
                           for i, sid in enumerate(enc.sequence_ids)])
    start_logits = out.start_logits[0].masked_fill(~is_ctx, -1e9)
    end_logits = out.end_logits[0].masked_fill(~is_ctx, -1e9)
    # 取最优合法 span
    best = (None, -1e18)
    starts = start_logits.topk(10).indices.tolist()
    ends = end_logits.topk(10).indices.tolist()
    for s in starts:
        for e in ends:
            if s <= e <= s + max_ans_len:
                score = (start_logits[s] + end_logits[e]).item()
                if score > best[1]:
                    best = ((s, e), score)
    if best[0] is None:
        return "", best[1]
    s, e = best[0]
    return context[offsets[s][0]:offsets[e][1]], best[1]


def main():
    text_file = sys.argv[1] if len(sys.argv) > 1 else "book/chat.txt"
    gold_file = sys.argv[2] if len(sys.argv) > 2 else None
    text = Path(text_file).read_text(encoding="utf-8")

    tokenizer, model = load_model()
    units = split_units(text)
    quote_idxs = [i for i, u in enumerate(units) if u[1]]

    gold = None
    if gold_file:
        gold = [q["speaker"] for q in json.loads(Path(gold_file).read_text())["quotes"]]

    correct = 0
    for n, qi in enumerate(quote_idxs):
        question, context = build_sample(units, qi)
        answer, score = predict_span(tokenizer, model, question, context)
        quote_text = units[qi][0][1:-1]
        if gold:
            g = gold[n]
            # 宽匹配：抽取span包含金标名或反之（如"田芸的父亲"~"田叔"按规范名判错）
            ok = bool(answer) and (g in answer or answer in g)
            correct += ok
            print(f"  {'✅' if ok else '❌'} 预测={answer or '∅':　<6} 金标={g:　<4} score={score:6.1f}  “{quote_text[:20]}”")
        else:
            print(f"  预测={answer or '∅':　<6} score={score:6.1f}  “{quote_text[:20]}”")
    if gold:
        print(f"\nCSI(L2 单独) 准确率: {correct}/{len(quote_idxs)} = {correct/len(quote_idxs):.0%}")


if __name__ == "__main__":
    main()
