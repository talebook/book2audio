"""小说TXT解析：章节分割 + 对白/旁白切分"""

import re
from dataclasses import dataclass
from typing import List

CHAPTER_RE = re.compile(r"^\s*(第[0-9一二三四五六七八九十百千零两]+章[^\n]*)$", re.M)
# 中文对白引号（全角弯引号）
QUOTE_RE = re.compile(r"“([^”]*)”")


@dataclass
class Chapter:
    num: int          # 序号（按出现顺序，从1开始）
    title: str
    content: str


@dataclass
class Segment:
    kind: str         # "narration" | "dialogue"
    text: str


def split_chapters(text: str) -> List[Chapter]:
    """按 `第X章` 标题行分割章节，标题前的内容（书名页等）丢弃。"""
    matches = list(CHAPTER_RE.finditer(text))
    chapters = []
    for i, m in enumerate(matches):
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        chapters.append(Chapter(num=i + 1, title=m.group(1).strip(), content=text[start:end].strip()))
    return chapters


def split_segments(content: str) -> List[Segment]:
    """将章节正文切分为旁白/对白片段，连续同类片段合并。"""
    segments: List[Segment] = []

    def push(kind: str, text: str):
        text = text.strip()
        if not text:
            return
        if segments and segments[-1].kind == kind:
            segments[-1].text += text if kind == "dialogue" else ("\n" + text)
        else:
            segments.append(Segment(kind, text))

    for para in content.splitlines():
        para = para.strip()
        if not para:
            continue
        pos = 0
        for m in QUOTE_RE.finditer(para):
            push("narration", para[pos:m.start()])
            push("dialogue", m.group(1))
            pos = m.end()
        push("narration", para[pos:])
    return segments
