from pathlib import Path
import subprocess

import whisper
from celery import shared_task

OUTPUT_DIR = Path("/app/storage/outputs")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def format_timestamp(seconds: float) -> str:
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    milliseconds = int((seconds - int(seconds)) * 1000)
    return f"{hours:02}:{minutes:02}:{secs:02},{milliseconds:03}"


@shared_task(name="process_video_task")
def process_video_task(file_path: str, original_filename: str):
    input_path = Path(file_path)

    if not input_path.exists():
        raise RuntimeError(f"Input file does not exist: {input_path}")

    model = whisper.load_model("base")
    result = model.transcribe(input_path.as_posix(), fp16=False)

    base_name = Path(original_filename).stem
    text_path = OUTPUT_DIR / f"{base_name}.txt"
    srt_path = OUTPUT_DIR / f"{base_name}.srt"
    video_output_path = OUTPUT_DIR / f"captioned_{base_name}.mp4"

    with open(text_path, "w", encoding="utf-8") as f:
        f.write(result["text"])

    segments = result.get("segments", [])
    with open(srt_path, "w", encoding="utf-8") as f:
        for i, seg in enumerate(segments, start=1):
            start = format_timestamp(seg["start"])
            end = format_timestamp(seg["end"])
            text = seg["text"].strip()
            f.write(f"{i}\n{start} --> {end}\n{text}\n\n")

    command = [
        "ffmpeg",
        "-i",
        input_path.as_posix(),
        "-vf",
        f"subtitles={srt_path.as_posix()}",
        "-c:a",
        "copy",
        video_output_path.as_posix(),
        "-y",
    ]

    completed = subprocess.run(command, capture_output=True, text=True)

    if completed.returncode != 0:
        raise RuntimeError(f"FFmpeg subtitle burn-in failed: {completed.stderr}")

    return {
        "message": "Video transcribed and subtitles burned successfully",
        "text_file": text_path.as_posix().replace("/app/", ""),
        "srt_file": srt_path.as_posix().replace("/app/", ""),
        "video_file": video_output_path.as_posix().replace("/app/", ""),
    }