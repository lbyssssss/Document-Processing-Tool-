export interface ConversionOptions {
  preserve_formatting: boolean
  quality?: number
  password?: string
  include_annotations?: boolean
}

export interface ConversionResult {
  success: boolean
  output_path?: string
  output_format: string
  warnings: string[]
  error?: string
}

export interface SearchOptions {
  case_sensitive: boolean
  whole_word: boolean
  regex: boolean
}

export interface SearchResult {
  page_index: number
  text: string
  position: {
    x: number
    y: number
    width: number
    height: number
  }
}

export type DocumentType = 'pdf' | 'word' | 'excel' | 'ppt' | 'image'

export interface Rectangle {
  x: number
  y: number
  width: number
  height: number
}

export interface Annotation {
  id: string
  document_id: string
  page_index: number
  position: Rectangle
  content: string
  author: string
  color: string
  created_at: string
  updated_at: string
}

export interface Page {
  index: number
  width: number
  height: number
  rotation: number
  thumbnail: string
  content?: any
}
