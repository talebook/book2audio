import argparse
from pathlib import Path

from .pipeline import run


def parse_range(s: str) -> range:
    if "-" in s:
        a, b = s.split("-", 1)
        return range(int(a), int(b) + 1)
    return range(int(s), int(s) + 1)


def main():
    p = argparse.ArgumentParser(prog="book2audio", description="小说TXT转有声书")
    p.add_argument("--input", "-i", type=Path, required=True, help="小说TXT文件")
    p.add_argument("--chapters", "-c", default="1-3", help="章节范围，如 1-3 或 5")
    p.add_argument("--output", "-o", type=Path, required=True, help="输出MP4路径")
    p.add_argument("--keep-temp", action="store_true", help="保留中间音频文件")
    p.add_argument("--multi-voice", action="store_true",
                   help="按角色画像分配音色（说话人识别+L3画像，需 models/csi-v1 可获得最佳归属）")
    args = p.parse_args()
    run(args.input, args.output, parse_range(args.chapters), args.keep_temp,
        multi_voice=args.multi_voice)


if __name__ == "__main__":
    main()
