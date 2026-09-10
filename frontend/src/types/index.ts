export interface UploadResponse {
  message: string
  task_id: string
  stored_filename: string
  target_language?: string
  file_path: string
}

export interface JobResult {
  message?: string
  detected_language?: string
  target_language?: string
  text_file?: string
  srt_file?: string
  video_file?: string
  error?: string
  traceback?: string
}

export interface JobStatusResponse {
  task_id: string
  status: 'PENDING' | 'STARTED' | 'SUCCESS' | 'FAILURE'
  result: JobResult | null
}