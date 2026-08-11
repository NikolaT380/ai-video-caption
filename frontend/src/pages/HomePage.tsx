import { api } from '../api/client'
import { useVideoProcessing } from '../hooks/useVideoProcessing'

export const HomePage = () => {
  const {
    file,
    setFile,
    taskId,
    status,
    jobResult,
    errorMessage,
    startProcessing,
    resetState,
  } = useVideoProcessing()

  return (
    <main className="page">
      <section className="card">
        <h1>AI Video Captioning Platform</h1>
        <p className="subtitle">
          Прикачи видео, почекај обработка и преземи транскрипт, титлови и готово видео.
        </p>

        <div className="upload-box">
          <label htmlFor="videoFile" className="file-label">
            Избери видео
          </label>
          <input
            id="videoFile"
            type="file"
            accept="video/*"
            onChange={(e) => setFile(e.target.files?.[0] ?? null)}
          />

          {file && (
            <p className="file-name">
              Избран фајл: <strong>{file.name}</strong>
            </p>
          )}

          <div className="actions">
            <button
              className="primary-btn"
              onClick={startProcessing}
              disabled={!file || status === 'UPLOADING' || status === 'PROCESSING'}
            >
              Прикачи и процесирај
            </button>

            <button className="secondary-btn" onClick={resetState}>
              Reset
            </button>
          </div>
        </div>

        <div className="status-box">
          <h2>Статус</h2>
          <p>
            UI статус: <strong>{status}</strong>
          </p>

          {taskId && (
            <p>
              Task ID: <code>{taskId}</code>
            </p>
          )}

          {status === 'UPLOADING' && <p>Видеото се прикачува...</p>}
          {status === 'PROCESSING' && <p>Видеото се обработува. Ова може да потрае.</p>}
          {status === 'ERROR' && <p className="error-text">{errorMessage}</p>}
          {status === 'SUCCESS' && <p className="success-text">Процесирањето е успешно завршено.</p>}
        </div>

        {jobResult && (
          <div className="results-box">
            <h2>Резултати</h2>
            <p>{jobResult.message}</p>

            <div className="download-links">
              <a
                href={api.getOutputUrl(jobResult.video_file)}
                target="_blank"
                rel="noreferrer"
              >
                Преземи MP4 видео
              </a>

              <a
                href={api.getOutputUrl(jobResult.srt_file)}
                target="_blank"
                rel="noreferrer"
              >
                Преземи SRT титлови
              </a>

              <a
                href={api.getOutputUrl(jobResult.text_file)}
                target="_blank"
                rel="noreferrer"
              >
                Преземи TXT транскрипт
              </a>
            </div>

            <div className="preview-box">
              <h3>Преглед на готово видео</h3>
              <video controls width="100%" src={api.getOutputUrl(jobResult.video_file)} />
            </div>
          </div>
        )}
      </section>
    </main>
  )
}