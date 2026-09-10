import { useEffect, useState } from 'react'
import { api } from '../api/client'
import type { JobResult } from '../types'

type UiStatus = 'IDLE' | 'UPLOADING' | 'PROCESSING' | 'SUCCESS' | 'ERROR'

export const useVideoProcessing = () => {
  const [file, setFile] = useState<File | null>(null)
  const [targetLanguage, setTargetLanguage] = useState<string>('original')
  const [taskId, setTaskId] = useState<string | null>(null)
  const [status, setStatus] = useState<UiStatus>('IDLE')
  const [jobResult, setJobResult] = useState<JobResult | null>(null)
  const [errorMessage, setErrorMessage] = useState<string>('')

  useEffect(() => {
    if (!taskId || status !== 'PROCESSING') return

    const intervalId = window.setInterval(async () => {
      try {
        const data = await api.checkJobStatus(taskId)

        if (data.status === 'SUCCESS') {
          setStatus('SUCCESS')
          setJobResult(data.result)
          window.clearInterval(intervalId)
        } else if (data.status === 'FAILURE') {
          setStatus('ERROR')
          const error =
            typeof data.result === 'object' && data.result && 'error' in data.result
              ? String(data.result.error ?? 'Процесирањето не успеа.')
              : 'Процесирањето не успеа.'
          setErrorMessage(error)
          window.clearInterval(intervalId)
        }
      } catch {
        setStatus('ERROR')
        setErrorMessage('Грешка при проверка на статусот.')
        window.clearInterval(intervalId)
      }
    }, 3000)

    return () => window.clearInterval(intervalId)
  }, [taskId, status])

  const startProcessing = async () => {
    if (!file) return

    try {
      setErrorMessage('')
      setJobResult(null)
      setStatus('UPLOADING')

      const data = await api.uploadVideo(file, targetLanguage)
      setTaskId(data.task_id)
      setStatus('PROCESSING')
    } catch (err: any) {
      setStatus('ERROR')
      setErrorMessage(err.message || 'Upload не успеа.')
    }
  }

  const resetState = () => {
    setFile(null)
    setTargetLanguage('original')
    setTaskId(null)
    setStatus('IDLE')
    setJobResult(null)
    setErrorMessage('')
  }

  return {
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
  }
}