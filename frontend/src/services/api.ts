import axios from 'axios'
import type { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios'

const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'

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
    const res = await apiClient.post('/conversion/pdf-to-word', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return res.data
  },

  async wordToPdf(file: File, options?: any) {
    const formData = new FormData()
    formData.append('file', file)
    const res = await apiClient.post('/conversion/word-to-pdf', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return res.data
  },

  async pdfToExcel(file: File, options?: any) {
    const formData = new FormData()
    formData.append('file', file)
    const res = await apiClient.post('/conversion/pdf-to-excel', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return res.data
  },

  async excelToPdf(file: File, options?: any) {
    const formData = new FormData()
    formData.append('file', file)
    const res = await apiClient.post('/conversion/excel-to-pdf', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return res.data
  },

  async pdfToPpt(file: File, options?: any) {
    const formData = new FormData()
    formData.append('file', file)
    const res = await apiClient.post('/conversion/pdf-to-ppt', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return res.data
  },

  async pptToPdf(file: File, options?: any) {
    const formData = new FormData()
    formData.append('file', file)
    const res = await apiClient.post('/conversion/ppt-to-pdf', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return res.data
  },

  async pdfToImages(file: File, options?: any) {
    const formData = new FormData()
    formData.append('file', file)
    if (options?.quality) formData.append('quality', options.quality.toString())
    if (options?.dpi) formData.append('dpi', options.dpi.toString())
    const res = await apiClient.post('/conversion/pdf-to-images', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return res.data
  },

  async imagesToPdf(files: File[], options?: any) {
    const formData = new FormData()
    files.forEach(file => formData.append('files', file))
    const res = await apiClient.post('/conversion/images-to-pdf', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return res.data
  },

  // 搜索
  async search(documentId: string, query: string, options?: any) {
    const res = await apiClient.get(`/search/${documentId}`, {
      params: { query, ...options },
    })
    return res.data
  },

  async buildIndex(documentId: string, file: File) {
    const formData = new FormData()
    formData.append('file', file)
    const res = await apiClient.post(`/search/index/${documentId}`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return res.data
  },

  async getIndexInfo(documentId: string) {
    const res = await apiClient.get(`/search/index/${documentId}/info`)
    return res.data
  },

  async deleteIndex(documentId: string) {
    const res = await apiClient.delete(`/search/index/${documentId}`)
    return res.data
  },

  // 批注
  async getAnnotations(documentId: string) {
    const res = await apiClient.get(`/annotation/${documentId}`)
    return res.data
  },

  async getPageAnnotations(documentId: string, pageIndex: number) {
    const res = await apiClient.get(`/annotation/${documentId}/${pageIndex}`)
    return res.data
  },

  async createAnnotation(annotation: any) {
    const res = await apiClient.post('/annotation', annotation)
    return res.data
  },

  async updateAnnotation(annotationId: string, documentId: string, annotation: any) {
    const res = await apiClient.put(`/annotation/${annotationId}?document_id=${documentId}`, annotation)
    return res.data
  },

  async deleteAnnotation(annotationId: string, documentId: string) {
    const res = await apiClient.delete(`/annotation/${annotationId}?document_id=${documentId}`)
    return res.data
  },

  async exportAnnotations(documentId: string, includeAnnotations: boolean = true) {
    const res = await apiClient.post(`/annotation/export/${documentId}`, null, {
      params: { include_annotations: includeAnnotations },
    })
    return res.data
  },

  async batchCreateAnnotations(documentId: string, annotations: any[]) {
    const res = await apiClient.post(`/annotation/batch/${documentId}`, annotations)
    return res.data
  },

  // 页面管理
  async getPages(documentId: string) {
    const res = await apiClient.get(`/page/${documentId}`)
    return res.data
  },

  async getPage(documentId: string, pageNumber: number) {
    const res = await apiClient.get(`/page/${documentId}/${pageNumber}`)
    return res.data
  },

  async getPageThumbnail(documentId: string, pageNumber: number, size: number = 300) {
    const res = await apiClient.get(`/page/${documentId}/${pageNumber}/thumbnail`, {
      params: { size },
    })
    return res.data
  },

  async insertPage(documentId: string, pageNumber: number, file?: File) {
    const formData = new FormData()
    if (file) {
      formData.append('file', file)
    }
    const res = await apiClient.post(`/page/${documentId}/insert?page_number=${pageNumber}`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return res.data
  },

  async deletePage(documentId: string, pageNumber: number) {
    const res = await apiClient.delete(`/page/${documentId}/${pageNumber}`)
    return res.data
  },

  async movePage(documentId: string, pageNumber: number, newPageNumber: number) {
    const res = await apiClient.post(`/page/${documentId}/${pageNumber}/move`, null, {
      params: { new_page_number: newPageNumber },
    })
    return res.data
  },

  async rotatePage(documentId: string, pageNumber: number, degrees: number) {
    const res = await apiClient.post(`/page/${documentId}/${pageNumber}/rotate`, null, {
      params: { degrees },
    })
    return res.data
  },

  async mergePages(documentId: string, pageNumbers: number[]) {
    const res = await apiClient.post(`/page/${documentId}/merge`, { page_numbers: pageNumbers })
    return res.data
  },

  async splitPage(documentId: string, pageNumber: number, splitType: string = 'vertical') {
    const res = await apiClient.post(`/page/${documentId}/${pageNumber}/split`, null, {
      params: { split_type: splitType },
    })
    return res.data
  },

  async uploadDocumentForPageManagement(documentId: string, file: File) {
    const formData = new FormData()
    formData.append('file', file)
    const res = await apiClient.post(`/page/${documentId}/upload`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return res.data
  },

  // 拼接
  async uploadDocumentForMerge(filePath: string) {
    const res = await apiClient.post('/merge/upload-document', null, {
      params: { file_path: filePath },
    })
    return res.data
  },

  async getDocumentPages(documentId: string) {
    const res = await apiClient.get(`/merge/documents/${documentId}/pages`)
    return res.data
  },

  async selectPage(page: any) {
    const res = await apiClient.post('/merge/select-page', page)
    return res.data
  },

  async deselectPage(pageId: string) {
    const res = await apiClient.delete(`/merge/select-page/${pageId}`)
    return res.data
  },

  async selectPageRange(documentId: string, start: number, end: number) {
    const res = await apiClient.post('/merge/select-range', null, {
      params: { document_id: documentId, start, end },
    })
    return res.data
  },

  async toggleAllPages(documentId: string) {
    const res = await apiClient.post(`/merge/toggle-all/${documentId}`)
    return res.data
  },

  async reorderPage(pageId: string, newIndex: number) {
    const res = await apiClient.post('/merge/reorder', null, {
      params: { page_id: pageId, new_index: newIndex },
    })
    return res.data
  },

  async clearQueue() {
    const res = await apiClient.delete('/merge/queue')
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

  async previewMerge() {
    const res = await apiClient.get('/merge/preview')
    return res.data
  },

  // 批量处理
  async batchUpload(files: File[]) {
    const formData = new FormData()
    files.forEach(file => formData.append('files', file))
    const res = await apiClient.post('/batch/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return res.data
  },

  async batchConvert(
    files: File[],
    targetFormat: string = 'pdf',
    preserveFormatting: boolean = true,
    quality?: number,
    dpi?: number
  ) {
    const formData = new FormData()
    files.forEach(file => formData.append('files', file))
    formData.append('target_format', targetFormat)
    formData.append('preserve_formatting', preserveFormatting.toString())
    if (quality !== undefined) formData.append('quality', quality.toString())
    if (dpi !== undefined) formData.append('dpi', dpi.toString())
    const res = await apiClient.post('/batch/convert', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return res.data
  },

  async getBatchStatus(taskId: string) {
    const res = await apiClient.get(`/batch/status/${taskId}`)
    return res.data
  },

  async cancelBatchTask(taskId: string) {
    const res = await apiClient.post(`/batch/cancel/${taskId}`)
    return res.data
  },

  async deleteBatchTask(taskId: string) {
    const res = await apiClient.delete(`/batch/task/${taskId}`)
    return res.data
  },

  async listBatchTasks() {
    const res = await apiClient.get('/batch/tasks')
    return res.data
  },

  async batchMergeFiles(files: File[]) {
    const formData = new FormData()
    files.forEach(file => formData.append('files', file))
    const res = await apiClient.post('/batch/merge', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return res.data
  },
}
