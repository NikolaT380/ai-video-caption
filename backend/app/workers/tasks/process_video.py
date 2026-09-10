from pathlib import Path
import logging
import subprocess
import time

import whisper
from celery import shared_task
from deep_translator import GoogleTranslator

OUTPUT_DIR = Path("/app/storage/outputs")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

logger = logging.getLogger(__name__)

SUPPORTED_TARGET_LANGUAGES = {
    "original",
    "mk",
    "en",
}

TRANSLATION_MAX_RETRIES = 4
TRANSLATION_INITIAL_DELAY_SECONDS = 1.0
TRANSLATION_REQUEST_DELAY_SECONDS = 0.8


def format_timestamp(seconds: float) -> str:
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    milliseconds = int((seconds - int(seconds)) * 1000)

    return f"{hours:02}:{minutes:02}:{secs:02},{milliseconds:03}"


def clean_filename(filename: str) -> str:
    return Path(filename).stem.replace(" ", "_")


def translate_segment(
    text: str,
    source_language: str,
    target_language: str,
) -> str:

    if not text.strip():
        return text

    if source_language == target_language:
        return text

    for attempt in range(TRANSLATION_MAX_RETRIES):
        try:
            translator = GoogleTranslator(
                source=source_language,
                target=target_language,
            )

            translated_text = translator.translate(text)

            if translated_text and translated_text.strip():
                return translated_text.strip()

            raise RuntimeError("Translation service returned an empty response")

        except Exception as exc:
            delay = TRANSLATION_INITIAL_DELAY_SECONDS * (2 ** attempt)

            logger.warning(
                "Translation attempt %s/%s failed. Source=%s, target=%s, text=%r, error=%s",
                attempt + 1,
                TRANSLATION_MAX_RETRIES,
                source_language,
                target_language,
                text[:100],
                str(exc),
            )

            if attempt < TRANSLATION_MAX_RETRIES - 1:
                time.sleep(delay)

    logger.error(
        "Translation failed after %s attempts. Keeping original text: %r",
        TRANSLATION_MAX_RETRIES,
        text[:200],
    )

    return text


@shared_task(name="process_video_task")
def process_video_task(
    file_path: str,
    original_filename: str,
    target_language: str = "original",
):
    input_path = Path(file_path)

    if not input_path.exists():
        raise RuntimeError(f"Input file does not exist: {input_path}")

    if target_language not in SUPPORTED_TARGET_LANGUAGES:
        raise RuntimeError(
            f"Unsupported target language: {target_language}. "
            f"Available options: {', '.join(sorted(SUPPORTED_TARGET_LANGUAGES))}"
        )

    logger.info("Loading Whisper model...")
    model = whisper.load_model("base")

    logger.info("Starting transcription for: %s", input_path.name)
    result = model.transcribe(
        input_path.as_posix(),
        fp16=False,
        task="transcribe",
    )

    detected_language = result.get("language", "en")
    segments = result.get("segments", [])

    should_translate = (
        target_language != "original"
        and target_language != detected_language
    )

    output_language = (
        detected_language if target_language == "original" else target_language
    )

    base_name = clean_filename(original_filename)
    filename_suffix = f"_{output_language}"

    text_path = OUTPUT_DIR / f"{base_name}{filename_suffix}.txt"
    srt_path = OUTPUT_DIR / f"{base_name}{filename_suffix}.srt"
    video_output_path = OUTPUT_DIR / f"captioned_{base_name}{filename_suffix}.mp4"

    translated_count = 0
    untranslated_count = 0
    subtitle_lines = []
    transcript_lines = []

    logger.info(
        "Processing captions. Detected language=%s, requested target=%s, translation=%s",
        detected_language,
        target_language,
        should_translate,
    )

    for index, segment in enumerate(segments, start=1):
        start_time = format_timestamp(segment["start"])
        end_time = format_timestamp(segment["end"])
        original_text = segment["text"].strip()

        caption_text = original_text

        if should_translate and original_text:
            caption_text = translate_segment(
                text=original_text,
                source_language=detected_language,
                target_language=target_language,
            )

            if caption_text == original_text:
                untranslated_count += 1
            else:
                translated_count += 1

            time.sleep(TRANSLATION_REQUEST_DELAY_SECONDS)

        subtitle_lines.append(
            f"{index}\n{start_time} --> {end_time}\n{caption_text}\n"
        )
        transcript_lines.append(caption_text)

    with open(srt_path, "w", encoding="utf-8") as srt_file:
        srt_file.write("\n".join(subtitle_lines))

    with open(text_path, "w", encoding="utf-8") as text_file:
        text_file.write("\n".join(transcript_lines))

    logger.info("Burning subtitles into video with FFmpeg...")

    ffmpeg_command = [
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

    completed = subprocess.run(
        ffmpeg_command,
        capture_output=True,
        text=True,
    )

    if completed.returncode != 0:
        logger.error("FFmpeg failed: %s", completed.stderr)
        raise RuntimeError(
            f"FFmpeg subtitle burn-in failed: {completed.stderr}"
        )

    message = (
        f"Video processed successfully. "
        f"Detected language: {detected_language}. "
        f"Caption language: {output_language}."
    )

    # if should_translate:
    #     message += (
    #         f" Translated segments: {translated_count}. "
    #         f"Segments kept in original language after failed retries: "
    #         f"{untranslated_count}."
    #     )

    return {
        "message": message,
        "detected_language": detected_language,
        "target_language": output_language,
        "translated_segments": translated_count,
        "untranslated_segments": untranslated_count,
        "text_file": text_path.as_posix().replace("/app/", ""),
        "srt_file": srt_path.as_posix().replace("/app/", ""),
        "video_file": video_output_path.as_posix().replace("/app/", ""),
    }