"""端到端流水线：TXT -> 章节 -> 对白/旁白 -> edge-tts 合成 -> ffmpeg 拼接为 MP4 有声书"""

import asyncio
import json
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import List

import edge_tts

from .parser import Chapter, split_chapters, split_segments

# 音色配置：旁白用沉稳男声，对白用年轻男声做区分（后续接入说话人识别后按角色分配）
NARRATOR_VOICE = "zh-CN-YunjianNeural"
DIALOGUE_VOICE = "zh-CN-YunxiNeural"

CONCURRENCY = 4
MAX_RETRIES = 3


async def _synth_one(text: str, voice: str, out_path: Path, sem: asyncio.Semaphore):
    async with sem:
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                await edge_tts.Communicate(text, voice).save(str(out_path))
                if out_path.stat().st_size > 0:
                    return
            except Exception as e:
                if attempt == MAX_RETRIES:
                    raise RuntimeError(f"TTS failed after {MAX_RETRIES} tries: {text[:30]}...") from e
                await asyncio.sleep(2 * attempt)


async def synth_chapter(chapter: Chapter, work_dir: Path) -> Path:
    """合成单章音频，返回章节 mp3 路径。"""
    segments = split_segments(chapter.content)
    # 章节标题作为开场旁白
    parts = [("narration", chapter.title)] + [(s.kind, s.text) for s in segments]

    sem = asyncio.Semaphore(CONCURRENCY)
    seg_dir = work_dir / f"ch{chapter.num:04d}"
    seg_dir.mkdir(parents=True, exist_ok=True)
    tasks = []
    seg_files = []
    for i, (kind, text) in enumerate(parts):
        voice = NARRATOR_VOICE if kind == "narration" else DIALOGUE_VOICE
        f = seg_dir / f"{i:05d}.mp3"
        seg_files.append(f)
        tasks.append(_synth_one(text, voice, f, sem))
    await asyncio.gather(*tasks)

    # ffmpeg concat 合并段落
    list_file = seg_dir / "list.txt"
    list_file.write_text("".join(f"file '{f.resolve()}'\n" for f in seg_files))
    chapter_mp3 = work_dir / f"chapter_{chapter.num:04d}.mp3"
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0",
         "-i", str(list_file), "-c", "copy", str(chapter_mp3)],
        check=True,
    )
    return chapter_mp3


def _duration_ms(path: Path) -> int:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "json", str(path)],
        check=True, capture_output=True, text=True,
    )
    return int(float(json.loads(out.stdout)["format"]["duration"]) * 1000)


def assemble_mp4(chapters: List[Chapter], chapter_files: List[Path], output: Path, work_dir: Path):
    """拼接所有章节并编码为带章节标记的 MP4（AAC）。"""
    list_file = work_dir / "all_chapters.txt"
    list_file.write_text("".join(f"file '{f.resolve()}'\n" for f in chapter_files))

    # 生成 FFMETADATA 章节标记
    meta_lines = [";FFMETADATA1", "title=玄鉴仙族", "artist=book2audio"]
    start = 0
    for ch, f in zip(chapters, chapter_files):
        end = start + _duration_ms(f)
        meta_lines += ["[CHAPTER]", "TIMEBASE=1/1000", f"START={start}", f"END={end}", f"title={ch.title}"]
        start = end
    meta_file = work_dir / "metadata.txt"
    meta_file.write_text("\n".join(meta_lines))

    output.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0",
         "-i", str(list_file), "-i", str(meta_file), "-map_metadata", "1",
         "-c:a", "aac", "-b:a", "64k", str(output)],
        check=True,
    )


def run(input_txt: Path, output: Path, chapter_range: range, keep_temp: bool = False):
    text = input_txt.read_text(encoding="utf-8")
    all_chapters = split_chapters(text)
    chapters = [c for c in all_chapters if c.num in chapter_range]
    if not chapters:
        raise SystemExit(f"未找到指定章节（全书共 {len(all_chapters)} 章）")
    print(f"共 {len(all_chapters)} 章，本次合成 {len(chapters)} 章: {chapters[0].title} .. {chapters[-1].title}")

    work_dir = Path(tempfile.mkdtemp(prefix="book2audio_"))
    try:
        chapter_files = []
        for ch in chapters:
            print(f"[{ch.num}/{chapters[-1].num}] 合成 {ch.title} ({len(ch.content)} 字)...")
            chapter_files.append(asyncio.run(synth_chapter(ch, work_dir)))
        print("拼接并编码 MP4...")
        assemble_mp4(chapters, chapter_files, output, work_dir)
        print(f"完成: {output}")
    finally:
        if not keep_temp:
            shutil.rmtree(work_dir, ignore_errors=True)
