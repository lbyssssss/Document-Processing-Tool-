import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export interface Document {
  id: string
  name: string
  type: string
  size: number
  file_path: string
  page_count: number
  created_at: string
  thumbnail_path?: string
}

export const useDocumentStore = defineStore('document', () => {
  const documents = ref<Document[]>([])
  const selectedDocument = ref<Document | null>(null)

  const documentCount = computed(() => documents.value.length)

  function addDocument(document: Document) {
    documents.value.push(document)
  }

  function removeDocument(id: string) {
    const index = documents.value.findIndex(d => d.id === id)
    if (index > -1) {
      documents.value.splice(index, 1)
    }
  }

  function selectDocument(document: Document) {
    selectedDocument.value = document
  }

  function clearDocuments() {
    documents.value = []
    selectedDocument.value = null
  }

  return {
    documents,
    selectedDocument,
    documentCount,
    addDocument,
    removeDocument,
    selectDocument,
    clearDocuments,
  }
})
