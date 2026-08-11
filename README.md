# AI Video Captioning Platform

AI Video Captioning Platform е веб апликација за автоматска транскрипција на видео, генерирање `.srt` титлови и креирање видео со вградени captions.

## Tech Stack

- FastAPI
- React + TypeScript + Vite
- Celery
- Redis
- PostgreSQL
- Whisper
- FFmpeg
- Docker Compose

## Features

- Upload на видео фајл
- Асинхроно процесирање со Celery
- Автоматска транскрипција со Whisper
- Генерирање `.txt` transcript
- Генерирање `.srt` subtitles
- Burn-in на subtitles во финално `.mp4` видео
- Polling на job status од frontend

## Project Structure

```text
ai-video-caption/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── routes/
│   │   │       ├── jobs.py
│   │   │       └── videos.py
│   │   ├── core/
│   │   │   └── celery_app.py
│   │   ├── workers/
│   │   │   └── tasks/
│   │   │       └── process_video.py
│   │   └── main.py
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   ├── hooks/
│   │   ├── pages/
│   │   ├── types/
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   └── index.css
├── storage/
│   ├── uploads/
│   └── outputs/
└── docker-compose.yml
```

## System Flow

1. Корисникот прикачува видео преку frontend.
2. FastAPI го зачувува видеото во `storage/uploads`.
3. API креира Celery task и враќа `task_id`.
4. Frontend периодично го проверува статусот преку `/api/jobs/{task_id}`.
5. Celery worker го зема видеото, прави транскрипција со Whisper и креира `.txt` и `.srt`.
6. FFmpeg прави ново видео со вградени subtitles.
7. Frontend прикажува download линкови за резултатите.

## How to Run

### 1. Start Docker services

```bash
docker compose up --build
```

### 2. Start frontend

```bash
cd frontend
npm install
npm run dev
```

### 3. Open the app

- Frontend: `http://localhost:5173`
- FastAPI docs: `http://127.0.0.1:8081/docs`

## API Endpoints

### Upload video
`POST /api/videos/upload`

### Check job status
`GET /api/jobs/{task_id}`

### Download output files
`GET /outputs/{filename}`

## Example Workflow

1. Upload `.mp4` video.
2. Receive `task_id`.
3. Poll status until `SUCCESS`.
4. Download:
   - transcript `.txt`
   - subtitles `.srt`
   - captioned video `.mp4`

## Notes

- Supported formats: `.mp4`, `.mov`, `.mkv`, `.avi`
- Output files are stored in `storage/outputs`
- Uploaded videos are stored in `storage/uploads`

## Future Improvements

- User authentication
- Progress percentage for jobs
- Multiple language support
- Subtitle style customization
- Database persistence for job history
- Delete old uploads and outputs automatically

## License

MIT