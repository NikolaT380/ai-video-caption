import type { JobStatusResponse, UploadResponse } from '../types'

const API_BASE_URL = 'http://127.0.0.1:8081'

export const api = {
    uploadVideo: async (file: File): Promise<UploadResponse> => {
    const formData = new FormData()
    formData.append('file', file)

    const response = await fetch(`${API_BASE_URL}/api/videos/upload`, {
      method: 'POST',
      body: formData,
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => null)
      const errorMessage = errorData?.detail || `Upload failed with status ${response.status}`
      throw new Error(errorMessage)
    }

    return response.json()
  },

  checkJobStatus: async (taskId: string): Promise<JobStatusResponse> => {
    const response = await fetch(`${API_BASE_URL}/api/jobs/${taskId}`)

    if (!response.ok) {
      throw new Error('Failed to fetch job status')
    }

    return response.json()
  },

  getOutputUrl: (filePath: string): string => {
    const fileName = filePath.split('/').pop()
    return `${API_BASE_URL}/outputs/${fileName}`
  },
}