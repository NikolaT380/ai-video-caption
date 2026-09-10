import { api } from '../api/client'
import { useVideoProcessing } from '../hooks/useVideoProcessing'

export const HomePage = () => {
  const {
    file,
    setFile,
    targetLanguage,
    setTargetLanguage,
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

        <div className="upload-box">
          <label htmlFor="videoFile" className="file-label">
            1. Избери видео:
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

          <div style={{ marginTop: '16px' }}>
            <label htmlFor="langSelect" className="file-label">
              2. Избери јазик на титловите:
            </label>
            <select
              id="langSelect"
              value={targetLanguage}
              onChange={(e) => setTargetLanguage(e.target.value)}
              style={{ padding: '8px 12px', borderRadius: '8px', width: '100%', marginTop: '4px' }}
            >
              <option value="original">Оригинален јазик (јазикот на видеото)</option>
              <option value="mk">Превод на Македонски (MK)</option>
              <option value="en">Превод на Англиски (EN)</option>
            </select>
          </div>

          <div className="actions">
            <button
              className="primary-btn"
              onClick={startProcessing}
              disabled={!file || status === 'UPLOADING' || status === 'PROCESSING'}
            >
              Процесирај
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
              Task ID: <strong>{taskId}</strong>
            </p>
          )}

          {status === 'UPLOADING' && <p>Видеото се прикачува...</p>}
          {status === 'PROCESSING' && <p>На видеото се прави превод и транскрипција. Ве молиме почекајте...</p>}
          {status === 'ERROR' && <p className="error-text">{errorMessage}</p>}
        </div>

        {status === 'SUCCESS' && jobResult && (
          <div className="results-box">
            <h2>Резултати</h2>
            <p>{jobResult.message}</p>

            <div className="download-links">
              {jobResult.text_file && (
                <a
                  href={api.getOutputUrl(jobResult.text_file)}
                  target="_blank"
                  rel="noreferrer"
                >
                  Преземи TXT
                </a>
              )}

              {jobResult.srt_file && (
                <a
                  href={api.getOutputUrl(jobResult.srt_file)}
                  target="_blank"
                  rel="noreferrer"
                >
                  Преземи SRT
                </a>
              )}

              {jobResult.video_file && (
                <a
                  href={api.getOutputUrl(jobResult.video_file)}
                  target="_blank"
                  rel="noreferrer"
                >
                  Преземи видео со титлови
                </a>
              )}
            </div>
          </div>
        )}
      </section>
    </main>
  )
}