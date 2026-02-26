import { defineStore } from 'pinia'
import { ref } from 'vue'

export interface SelectedPage {
  id: string
  document_id: string
  page_index: number
  original_document_name: string
  thumbnail: string
  page_width: number
  page_height: number
  rotation: number
}

export interface MergeConfig {
  page_size: string
  orientation: string
  output_file_name: string
  include_bookmarks: boolean
}

export const useMergeStore = defineStore('merge', () => {
  const queue = ref<SelectedPage[]>([])
  const config = ref<MergeConfig>({
    page_size: 'auto',
    orientation: 'keep-original',
    output_file_name: 'merged.pdf',
    include_bookmarks: false,
  })

  function addPage(page: SelectedPage) {
    queue.value.push(page)
  }

  function removePage(pageId: string) {
    const index = queue.value.findIndex(p => p.id === pageId)
    if (index > -1) {
      queue.value.splice(index, 1)
    }
  }

  function clearQueue() {
    queue.value = []
  }

  function updateConfig(newConfig: Partial<MergeConfig>) {
    config.value = { ...config.value, ...newConfig }
  }

  return {
    queue,
    config,
    addPage,
    removePage,
    clearQueue,
    updateConfig,
  }
})
