"""用 easytts 原版 CSI 推理管线（json2features + write_predictions）评估 csi-v1 模型。

依赖: git clone --depth 1 https://github.com/Warma10032/easytts /tmp/easytts_ref
目的: 验证模型本身的能力，定位 proto_csi.py 自实现与原管线的差异。
"""

import json
import sys
import collections
from pathlib import Path

import torch

ROOT = Path(__file__).resolve().parents[2]
EASYTTS = Path("/tmp/easytts_ref")
sys.path.insert(0, str(EASYTTS))

from src.speaker_identification.preprocess.text_preprocess import TextPreprocessor  # noqa: E402
from src.speaker_identification.csi.models.pytorch_modeling import BertConfig, BertForQuestionAnswering  # noqa: E402
from src.speaker_identification.csi.tokenizations import official_tokenization as tokenization  # noqa: E402
from src.speaker_identification.csi.preprocess.cmrc2018_preprocess import json2features  # noqa: E402
from src.speaker_identification.csi.evaluate.cmrc2018_output import write_predictions  # noqa: E402

MODEL_DIR = ROOT / "models/csi-v1"
WORK = Path(__file__).parent / "easytts_eval_work"
WORK.mkdir(exist_ok=True)


def build_dataset(text: str, pre_size=3, post_size=3):
    sentences, quotes_idx = TextPreprocessor.split_sentences(text, "遇到类句号标点一分")
    dataset = {"version": "v1.0", "data": []}
    quotes = []
    for idx in quotes_idx:
        pre, quote, post, q_ctx = TextPreprocessor.get_context(sentences, idx, pre_size, post_size)
        dataset["data"].append({"paragraphs": [{
            "id": f"sentence_{idx}",
            "context": f"{pre} {quote} {post}",
            "qas": [{"question": q_ctx, "id": f"sentence_{idx}",
                     "answers": [{"text": "说话人", "answer_start": 1}]}],
        }]})
        quotes.append(quote)
    return dataset, quotes


def main():
    text = Path(sys.argv[1] if len(sys.argv) > 1 else "book/chat.txt").read_text(encoding="utf-8")
    gold_file = sys.argv[2] if len(sys.argv) > 2 else None

    dataset, quotes = build_dataset(text)
    dev_file = WORK / "dataset.json"
    dev_file.write_text(json.dumps(dataset, ensure_ascii=False, indent=1))

    tokenizer = tokenization.BertTokenizer(vocab_file=str(MODEL_DIR / "vocab.txt"), do_lower_case=True)
    ex_file, feat_file = WORK / "examples.json", WORK / "features.json"
    for f in (ex_file, feat_file):
        f.unlink(missing_ok=True)
    json2features(str(dev_file), [str(ex_file), str(feat_file)], tokenizer, is_training=False, max_seq_length=512)
    eval_examples = json.load(open(ex_file))
    eval_features = json.load(open(feat_file))

    bert_config = BertConfig.from_json_file(str(MODEL_DIR / "config.json"))
    model = BertForQuestionAnswering(bert_config)
    state = torch.load(MODEL_DIR / "csi-v1.pth", map_location="cpu", weights_only=True)
    model.load_state_dict(state, strict=False)
    model.eval()

    RawResult = collections.namedtuple("RawResult", ["unique_id", "start_logits", "end_logits"])
    results = []
    with torch.no_grad():
        for f in eval_features:
            input_ids = torch.tensor([f["input_ids"]])
            input_mask = torch.tensor([f["input_mask"]])
            segment_ids = torch.tensor([f["segment_ids"]])
            start_logits, end_logits = model(input_ids, segment_ids, input_mask)
            results.append(RawResult(unique_id=int(f["unique_id"]),
                                     start_logits=start_logits[0].tolist(),
                                     end_logits=end_logits[0].tolist()))

    pred_file = WORK / "predictions.json"
    write_predictions(eval_examples, eval_features, results, n_best_size=6, max_answer_length=50,
                      do_lower_case=True, output_prediction_file=str(pred_file),
                      output_nbest_file=str(WORK / "nbest.json"))
    preds = json.load(open(pred_file))

    gold = None
    if gold_file:
        gold = [q["speaker"] for q in json.loads(Path(gold_file).read_text())["quotes"]]

    correct = 0
    for n, (qid, quote) in enumerate(zip([d["paragraphs"][0]["id"] for d in dataset["data"]], quotes)):
        ans = preds.get(qid, "")
        if gold:
            g = gold[n]
            ok = bool(ans) and (g in ans or ans in g)
            correct += ok
            print(f"  {'✅' if ok else '❌'} 预测={ans:　<8} 金标={g:　<4} “{quote[1:21]}”")
        else:
            print(f"  预测={ans:　<8} “{quote[1:21]}”")
    if gold:
        print(f"\neasytts原版管线 CSI 准确率: {correct}/{len(quotes)} = {correct/len(quotes):.0%}")


if __name__ == "__main__":
    main()
