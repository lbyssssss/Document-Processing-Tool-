import axios from 'axios'
import type { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios'

// 使用相对路径，由 vite 代理转发到后端
const baseURL = '/api/v1'

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

  async buildIndex(documentId: string) {
    const res = await apiClient.post(`/search/index/${documentId}`)
    return res.data
  },

  // 获取文档页面
  async getDocumentPages(documentId: string) {
    const res = await apiClient.get(`/merge/documents/${documentId}/pages`)
    return res.data
  },

  // 拼接
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

  // 批注
  async getAnnotations(documentId: string) {
    const res = await apiClient.get(`/annotation/${documentId}`)
    return res.data
  },

  async addAnnotation(documentId: string, annotation: any) {
    const res = await apiClient.post(`/annotation/${documentId}`, annotation)
    return res.data
  },

  async deleteAnnotation(documentId: string, annotationId: string) {
    const res = await apiClient.delete(`/annotation/${documentId}/${annotationId}`)
    return res.data
  },

  // 页面管理
  async uploadDocument(file: File) {
    const formData = new FormData()
    formData.append('file', file)
    const res = await apiClient.post('/merge/upload-document', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return res.data
  },

  async getPages(documentId: string) {
    const res = await apiClient.get(`/page/${documentId}/pages`)
    return res.data
  },

  async updatePage(documentId: string, pageId: string, operation: any) {
    const res = await apiClient.post(`/page/${documentId}/pages/${pageId}`, operation)
    return res.data
  },

  async addPage(documentId: string, page: any) {
    const res = await apiClient.post(`/page/${documentId}/pages`, page)
    return res.data
  },

  async getPageThumbnail(documentId: string, pageNumber: number) {
    const res = await apiClient.get(`/page/${documentId}/page/${pageNumber}/thumbnail`)
    return res.data
  },

  // 下载转换后的文件
  downloadConvertedFile(filename: string) {
    const url = `/api/v1/conversion/download/${filename}`
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  },
}
