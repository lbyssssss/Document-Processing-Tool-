<template>
  <div class="merge-view">
    <el-container>
      <el-header>
        <el-button @click="$router.back()">
          <el-icon><ArrowLeft /></el-icon>
          返回
        </el-button>
        <h2>文档拼接</h2>
      </el-header>
      <el-main>
        <el-row :gutter="20">
          <!-- 左侧：文档列表和页面选择 -->
          <el-col :span="16">
            <el-card class="document-list-card">
              <template #header>
                <div class="card-header">
                  <span>文档列表 ({{ documents.length }})</span>
                  <el-button size="small" type="primary" @click="showUploadDialog = true">
                    <el-icon><Plus /></el-icon>
                    添加文档
                  </el-button>
                </div>
              </template>

              <el-empty v-if="documents.length === 0" description="暂无文档，请点击右上角上传" />

              <el-tabs v-else v-model="activeDocumentId">
                <el-tab-pane
                  v-for="doc in documents"
                  :key="doc.id"
                  :label="doc.name"
                  :name="doc.id"
                >
                  <template #label>
                    <span class="tab-label">
                      {{ doc.name }}
                      <el-button
                        size="small"
                        text
                        type="danger"
                        @click.stop="removeDocument(doc.id)"
                      >
                        <el-icon><Close /></el-icon>
                      </el-button>
                    </span>
                  </template>

                  <div class="page-grid">
                    <div
                      v-for="(page, index) in doc.pages"
                      :key="index"
                      class="page-item"
                      :class="{ selected: isPageSelected(doc.id, index) }"
                      @click="togglePageSelection(doc.id, index)"
                    >
                      <div class="page-thumbnail">
                        <img
                          v-if="page.thumbnail"
                          :src="page.thumbnail"
                          alt="页面缩略图"
                          class="page-thumbnail-img"
                        />
                        <el-icon v-else :size="40"><Document /></el-icon>
                      </div>
                      <span class="page-number">{{ index + 1 }}</span>
                      <el-icon v-if="isPageSelected(doc.id, index)" class="check-icon">
                        <CircleCheckFilled />
                      </el-icon>
                      <el-button
                        size="small"
                        circle
                        class="preview-btn"
                        @click.stop="showPagePreview(doc, index)"
                      >
                        <el-icon><ZoomIn /></el-icon>
                      </el-button>
                    </div>
                  </div>
                </el-tab-pane>
              </el-tabs>
            </el-card>
          </el-col>

          <!-- 右侧：拼接队列 -->
          <el-col :span="8">
            <el-card class="merge-queue-card">
              <template #header>
                <div class="card-header">
                  <span>拼接队列</span>
                  <el-tag type="info">{{ queue.length }} 页</el-tag>
                </div>
              </template>

              <div class="queue-list">
                <div
                  v-for="(page, index) in queue"
                  :key="page.id"
                  class="queue-item"
                >
                  <div class="queue-item-thumb">
                    <el-icon :size="24"><Document /></el-icon>
                  </div>
                  <div class="queue-item-info">
                    <div class="queue-item-name">{{ page.original_document_name }}</div>
                    <div class="queue-item-page">第 {{ page.page_index + 1 }} 页</div>
                    <div class="queue-item-actions">
                      <el-button
                        size="small"
                        circle
                        @click.stop="showPreview(page)"
                      >
                        预览
                      </el-button>
                    </div>
                  </div>
                  <el-button
                    size="small"
                    type="danger"
                    @click.stop="removeFromQueue(page.id)"
                  >
                    <el-icon><Delete /></el-icon>
                  </el-button>
                </div>

                <el-empty v-if="queue.length === 0" description="队列为空" :image-size="80" />
              </div>

              <div class="queue-actions">
                <el-button @click="clearQueue" :disabled="queue.length === 0">
                  清空队列
                </el-button>
                <el-button
                  type="primary"
                  @click="handleMerge"
                  :disabled="queue.length === 0"
                  :loading="merging"
                >
                  生成合并文档
                </el-button>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </el-main>
    </el-container>

    <!-- 上传对话框 -->
    <el-dialog v-model="showUploadDialog" title="上传文档" width="600px">
      <input
        ref="fileInputRef"
        type="file"
        accept=".pdf"
        multiple
        style="display: none"
        @change="handleFileInputChange"
      />
      <div class="upload-area" @click="fileInputRef?.click()">
        <el-icon :size="60"><UploadFilled /></el-icon>
        <div class="el-upload__text">
          支持批量上传 PDF 文件，最多 10 个
        </div>
      </div>
      <div v-if="selectedFiles.length > 0" class="selected-files">
        <div v-for="(file, index) in selectedFiles" :key="index" class="selected-file-item">
          <span>{{ file.name }}</span>
          <el-button size="small" text type="danger" @click.stop="removeSelectedFile(index)">
            <el-icon><Close /></el-icon>
          </el-button>
        </div>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showUploadDialog = false">取消</el-button>
          <el-button type="primary" @click="handleFileUpload" :loading="uploading">
            上传
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 页面预览对话框 -->
    <el-dialog v-model="showPreviewDialog" title="页面预览" width="800px">
      <div v-if="previewPage" class="preview-container">
        <p><strong>文档：</strong>{{ previewPage.original_document_name }}</p>
        <p><strong>页码：</strong>第 {{ previewPage.page_index + 1 }} 页</p>
        <div class="preview-image">
          <img v-if="previewPage.thumbnail" :src="previewPage.thumbnail" alt="页面预览" />
          <el-icon v-else :size="200"><Document /></el-icon>
        </div>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showPreviewDialog = false">关闭</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import {
  ArrowLeft,
  Plus,
  Delete,
  CircleCheckFilled,
  UploadFilled,
  Document,
  Close,
  ZoomIn,
} from '@element-plus/icons-vue'
import { useMergeStore } from '@/stores/merge'
import { api } from '@/services/api'
import { ElMessage } from 'element-plus'

const router = useRouter()
const mergeStore = useMergeStore()
const queue = computed(() => mergeStore.queue)

const activeDocumentId = ref('')
const showUploadDialog = ref(false)
const merging = ref(false)
const uploading = ref(false)

const documents = ref<any[]>([])
const showPreviewDialog = ref(false)
const previewPage = ref<any>(null)
const fileInputRef = ref<HTMLInputElement | null>(null)
const selectedFiles = ref<File[]>([])

async function handleFileUpload() {
  console.log('handleFileUpload 调用, selectedFiles:', selectedFiles.value)
  console.log('selectedFiles length:', selectedFiles.value.length)
  if (selectedFiles.value.length === 0) {
    ElMessage.warning('请选择文件')
    return
  }

  uploading.value = true

  try {
    console.log('准备上传的文件:', selectedFiles.value.length, '个')

    // 批量上传所有文件
    const uploadPromises = selectedFiles.value.map(async (file) => {
      console.log('上传文件:', file.name, file.size)
      const result = await api.uploadDocument(file)

      // 获取文档页面列表
      if (result.status === 'uploaded') {
        const documentId = result.document_id
        const pagesResult = await api.getDocumentPages(documentId)

        return {
          success: true,
          documentId,
          filename: result.filename,
          pages: pagesResult.pages || [],
        }
      }

      return null
    })

    const uploadResults = await Promise.all(uploadPromises)

    let successCount = 0
    uploadResults.forEach((result: any) => {
      if (result && result.success) {
        documents.value.push({
          id: result.documentId,
          name: result.filename,
          pages: result.pages || [],
        })
        if (documents.value.length === 1) {
          activeDocumentId.value = result.documentId
        }
        successCount++
      }
    })

    if (successCount > 0) {
      ElMessage.success(`成功上传 ${successCount} 个文档`)
      showUploadDialog.value = false
      // 清空上传文件列表
      selectedFiles.value = []
    } else {
      ElMessage.error('文档上传失败')
    }
  } catch (error: any) {
    ElMessage.error(`上传失败：${error.message}`)
  } finally {
    uploading.value = false
    selectedFiles.value = []
  }
}

function handleFileInputChange(event: Event) {
  const target = event.target as HTMLInputElement
  if (target.files) {
    const files = Array.from(target.files)
    console.log('handleFileInputChange 选择文件:', files.length, '个')
    selectedFiles.value = files
  }
}

function removeSelectedFile(index: number) {
  selectedFiles.value.splice(index, 1)
}

function isPageSelected(docId: string, pageIndex: number): boolean {
  return queue.value.some(
    p => p.document_id === docId && p.page_index === pageIndex
  )
}

async function togglePageSelection(docId: string, pageIndex: number) {
  const doc = documents.value.find(d => d.id === docId)
  if (!doc) return

  const pageId = `${docId}_${pageIndex}`

  if (isPageSelected(docId, pageIndex)) {
    await api.deselectPage(pageId)
    mergeStore.removePage(pageId)
  } else {
    const selectedPage = {
      id: pageId,
      document_id: docId,
      page_index: pageIndex,
      original_document_name: doc.name,
      thumbnail: doc.pages[pageIndex].thumbnail || '',
      page_width: doc.pages[pageIndex].width || 595.28,
      page_height: doc.pages[pageIndex].height || 841.89,
      rotation: doc.pages[pageIndex].rotation || 0,
    }
    await api.selectPage(selectedPage)
    mergeStore.addPage(selectedPage)
  }
}

async function removeFromQueue(pageId: string) {
  await api.deselectPage(pageId)
  mergeStore.removePage(pageId)
}

function clearQueue() {
  mergeStore.clearQueue()
}

function removeDocument(docId: string) {
  documents.value = documents.value.filter(d => d.id !== docId)

  queue.value.forEach((page: any) => {
    if (page.document_id === docId) {
      removeFromQueue(page.id)
    }
  })

  if (activeDocumentId.value === docId && documents.value.length > 0) {
    activeDocumentId.value = documents.value[0].id
  } else if (documents.value.length === 0) {
    activeDocumentId.value = ''
  }
}

function showPagePreview(doc: any, pageIndex: number) {
  previewPage.value = {
    original_document_name: doc.name,
    page_index: pageIndex,
    thumbnail: doc.pages[pageIndex]?.thumbnail || '',
  }
  showPreviewDialog.value = true
}

function showPreview(page: any) {
  previewPage.value = page
  showPreviewDialog.value = true
}

async function handleMerge() {
  merging.value = true
  try {
    const config = mergeStore.config
    const result = await api.mergeDocuments(config)
    if (result.success) {
      ElMessage.success(`合并成功！共 ${result.total_pages} 页`)
      // 自动下载合并后的文件
      if (result.output_path) {
        // 从 output_path 中提取文件名（移除任何路径前缀）
        const filename = result.output_path.replace(/^.*[\/\\]/, '')
        // 使用 fetch GET 请求下载文件
        fetch(`/api/v1/merge/download/${filename}`)
          .then(response => response.blob())
          .then(blob => {
            const url = window.URL.createObjectURL(blob)
            const link = document.createElement('a')
            link.href = url
            link.download = filename
            link.click()
            window.URL.revokeObjectURL(url)
          })
      }
    } else {
      ElMessage.error(`合并失败：${result.error}`)
    }
  } catch (error: any) {
    ElMessage.error(`合并失败：${error.message}`)
  } finally {
    merging.value = false
  }
}
</script>

<style scoped>
.merge-view {
  height: 100vh;
}

.el-header {
  display: flex;
  align-items: center;
  gap: 16px;
  border-bottom: 1px solid #eee;
}

.el-main {
  padding: 24px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.tab-label {
  display: flex;
  align-items: center;
  gap: 8px;
}

.page-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
  gap: 12px;
  padding: 16px 0;
}

.page-item {
  position: relative;
  border: 2px solid #eee;
  border-radius: 6px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.2s;
  aspect-ratio: 0.707;
}

.page-item:hover {
  border-color: #409eff;
}

.page-item.selected {
  border-color: #409eff;
  background-color: #ecf5ff;
}

.page-thumbnail {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  background-color: #f5f5f5;
  color: #999;
}

.page-thumbnail-img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.page-number {
  position: absolute;
  bottom: 4px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(0, 0, 0, 0.6);
  color: white;
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 11px;
}

.check-icon {
  position: absolute;
  top: 4px;
  right: 4px;
  color: #409eff;
  background: white;
  border-radius: 50%;
}

.preview-btn {
  position: absolute;
  top: 4px;
  left: 4px;
  opacity: 0;
  transition: opacity 0.2s;
}

.page-item:hover .preview-btn {
  opacity: 1;
}

.queue-list {
  max-height: 450px;
  overflow-y: auto;
}

.queue-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px;
  border-bottom: 1px solid #eee;
}

.queue-item-thumb {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 40px;
  height: 56px;
  background-color: #f5f5f5;
  border-radius: 4px;
  color: #999;
}

.queue-item-info {
  flex: 1;
}

.queue-item-name {
  font-size: 14px;
  font-weight: 500;
}

.queue-item-page {
  font-size: 12px;
  color: #999;
  margin-top: 2px;
}

.queue-actions {
  display: flex;
  gap: 8px;
  margin-top: 16px;
}

.queue-actions .el-button {
  flex: 1;
}

.preview-container {
  text-align: center;
}

.preview-image {
  margin-top: 20px;
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 300px;
}

.preview-image img {
  max-width: 100%;
  max-height: 600px;
  border: 1px solid #eee;
  border-radius: 4px;
}

.upload-area {
  border: 2px dashed #d9d9d9;
  border-radius: 6px;
  padding: 40px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
}

.upload-area:hover {
  border-color: #409eff;
  background-color: #f5f7fa;
}

.selected-files {
  margin-top: 16px;
  max-height: 200px;
  overflow-y: auto;
}

.selected-file-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  background-color: #f5f7fa;
  border-radius: 4px;
  margin-bottom: 8px;
}
</style>
