import axios from 'axios'
import type { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios'

const baseURL = import.meta.env.VITE_API_BASE_URL || '/api/v1'

const apiClient: AxiosInstance = axios.create({
  baseURL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器
apiClient.interceptors.request.use(
  (config) => {
    // 如果是 FormData，删除 Content-Type，让浏览器自动设置 boundary
    if (config.data instanceof FormData) {
      delete config.headers['Content-Type']
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    return response
  },
  (error) => {
    const message = error.response?.data?.message || error.message || '请求失败'
    console.error('API Error:', message)
    return Promise.reject(error)
  }
)

export default apiClient

// API方法
export const api = {
  // 文档转换
  async pdfToWord(file: File, options?: any) {
    const formData = new FormData()
    formData.append('file', file)
    const res = await apiClient.post('/conversion/pdf-to-word', formData)
    return res.data
  },

  async wordToPdf(file: File, options?: any) {
    const formData = new FormData()
    formData.append('file', file)
    const res = await apiClient.post('/conversion/word-to-pdf', formData)
    return res.data
  },

  async pdfToExcel(file: File, options?: any) {
    const formData = new FormData()
    formData.append('file', file)
    const res = await apiClient.post('/conversion/pdf-to-excel', formData)
    return res.data
  },

  async excelToPdf(file: File, options?: any) {
    const formData = new FormData()
    formData.append('file', file)
    const res = await apiClient.post('/conversion/excel-to-pdf', formData)
    return res.data
  },

  async pdfToPpt(file: File, options?: any) {
    const formData = new FormData()
    formData.append('file', file)
    const res = await apiClient.post('/conversion/pdf-to-ppt', formData)
    return res.data
  },

  async pptToPdf(file: File, options?: any) {
    const formData = new FormData()
    formData.append('file', file)
    const res = await apiClient.post('/conversion/ppt-to-pdf', formData)
    return res.data
  },

  async pdfToImages(file: File, options?: any) {
    const formData = new FormData()
    formData.append('file', file)
    if (options?.quality) formData.append('quality', options.quality.toString())
    if (options?.dpi) formData.append('dpi', options.dpi.toString())
    const res = await apiClient.post('/conversion/pdf-to-images', formData)
    return res.data
  },

  async imagesToPdf(files: File[], options?: any) {
    const formData = new FormData()
    files.forEach(file => formData.append('files', file))
    const res = await apiClient.post('/conversion/images-to-pdf', formData)
    return res.data
  },

  // 搜索
  async search(documentId: string, query: string, options?: any) {
    const res = await apiClient.get(`/search/${documentId}`, {
      params: { query, ...options },
    })
    return res.data
  },

  async buildIndex(documentId: string) {
    const res = await apiClient.post(`/search/index/${documentId}`)
    return res.data
  },

  async getIndexInfo(documentId: string) {
    const res = await apiClient.get(`/search/index/${documentId}/info`)
    return res.data
  },

  // 批注
  async getAnnotations(documentId?: string) {
    const params = documentId ? { document_id: documentId } : {}
    const res = await apiClient.get('/annotation', { params })
    return res.data
  },

  async createAnnotation(annotation: any) {
    const res = await apiClient.post('/annotation', annotation)
    return res.data
  },

  async getAnnotation(annotationId: string) {
    const res = await apiClient.get(`/annotation/${annotationId}`)
    return res.data
  },

  async updateAnnotation(annotationId: string, annotation: any) {
    const res = await apiClient.put(`/annotation/${annotationId}`, annotation)
    return res.data
  },

  async deleteAnnotation(annotationId: string) {
    const res = await apiClient.delete(`/annotation/${annotationId}`)
    return res.data
  },

  async clearDocumentAnnotations(documentId: string) {
    const res = await apiClient.delete(`/annotation/document/${documentId}`)
    return res.data
  },

  async getAnnotationStats(documentId?: string) {
    const params = documentId ? { document_id: documentId } : {}
    const res = await apiClient.get('/annotation/stats', { params })
    return res.data
  },

  // 页面管理
  async getDocumentPagesInfo(documentId: string) {
    const res = await apiClient.get(`/page/document/${documentId}/info`)
    return res.data
  },

  async insertPage(documentId: string, request: any) {
    const res = await apiClient.post(`/page/${documentId}/insert`, request)
    return res.data
  },

  async deletePage(documentId: string, pageNumber: number) {
    const res = await apiClient.delete(`/page/${documentId}/${pageNumber}`)
    return res.data
  },

  async movePage(documentId: string, request: any) {
    const res = await apiClient.post(`/page/${documentId}/move`, request)
    return res.data
  },

  async rotatePage(documentId: string, pageNumber: number, request: any) {
    const res = await apiClient.post(`/page/${documentId}/${pageNumber}/rotate`, request)
    return res.data
  },

  async mergePages(documentId: string, request: any) {
    const res = await apiClient.post(`/page/${documentId}/merge`, request)
    return res.data
  },

  async splitPage(documentId: string, pageNumber: number) {
    const res = await apiClient.post(`/page/${documentId}/${pageNumber}/split`)
    return res.data
  },

  // 批量处理
  async batchConvert(files: File[], options?: any) {
    const formData = new FormData()
    files.forEach(file => formData.append('files', file))

    const params = options ? { ...options } : {}

    const res = await apiClient.post('/batch/convert', formData, { params })
    return res.data
  },

  async batchImagesToPdf(files: File[], options?: any) {
    const formData = new FormData()
    files.forEach(file => formData.append('files', file))

    const params = options ? { ...options } : {}

    const res = await apiClient.post('/batch/images-to-pdf', formData, { params })
    return res.data
  },

  async getBatchStatus(taskId: string) {
    const res = await apiClient.get(`/batch/status/${taskId}`)
    return res.data
  },

  async getBatchResult(taskId: string) {
    const res = await apiClient.get(`/batch/result/${taskId}`)
    return res.data
  },

  async cancelBatchTask(taskId: string) {
    const res = await apiClient.delete(`/batch/task/${taskId}`)
    return res.data
  },

  async listBatchTasks() {
    const res = await apiClient.get('/batch/tasks')
    return res.data
  },

  async cleanupOldTasks(maxAgeHours: number = 24) {
    const res = await apiClient.post('/batch/cleanup', {}, {
      params: { max_age_hours: maxAgeHours.toString() },
    })
    return res.data
  },

  // 拼接
  async uploadDocument(file: File) {
    const formData = new FormData()
    formData.append('file', file)
    const res = await apiClient.post('/merge/upload-document', formData)
    return res.data
  },

  async uploadDocumentsBatch(files: File[]) {
    const formData = new FormData()
    files.forEach(file => formData.append('files', file))
    const res = await apiClient.post('/merge/upload-documents-batch', formData)
    return res.data
  },

  async downloadMergedFile(filename: string) {
    const res = await apiClient.get(`/merge/download/${filename}`, {
      responseType: 'blob',
    })
    return res
  },

  async selectPage(page: any) {
    const res = await apiClient.post('/merge/select-page', page)
    return res.data
  },

  async deselectPage(pageId: string) {
    const res = await apiClient.delete(`/merge/select-page/${pageId}`)
    return res.data
  },

  async getQueue() {
    const res = await apiClient.get('/merge/queue')
    return res.data
  },

  async mergeDocuments(config: any) {
    const res = await apiClient.post('/merge/execute', config)
    return res.data
  },

  async getDocumentPages(documentId: string) {
    const res = await apiClient.get(`/merge/documents/${documentId}/pages`)
    return res.data
  },

  async deleteDocument(documentId: string) {
    const res = await apiClient.delete(`/merge/documents/${documentId}`)
    return res.data
  },
}

