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
        <!-- 上传文档对话框 -->
        <el-dialog v-model="showUploadDialog" title="上传文档" width="600px">
          <el-upload
            drag
            :auto-upload="false"
            :on-change="handleFileUpload"
            :file-list="uploadFileList"
            accept=".pdf"
            :limit="10"
            multiple
          >
            <el-icon :size="60"><UploadFilled /></el-icon>
            <div class="el-upload__text">
              将PDF文件拖到此处，或<em>点击上传</em>
            </div>
            <template #tip>
              <div class="el-upload__tip">
                只支持PDF格式，可批量上传多个文件
              </div>
            </template>
          </el-upload>
          <template #footer>
            <el-button @click="showUploadDialog = false">取消</el-button>
            <el-button type="primary" @click="confirmUpload" :loading="uploading">
              确定
            </el-button>
          </template>
        </el-dialog>

        <el-row :gutter="20">
          <!-- 左侧：文档列表和页面选择 -->
          <el-col :span="16">
            <el-card class="document-list-card">
              <template #header>
                <span>上传文档</span>
                <el-button size="small" type="primary" @click="showUploadDialog = true">
                  <el-icon><Plus /></el-icon>
                  添加文档
                </el-button>
              </template>

              <el-tabs v-model="activeDocumentId">
                <el-tab-pane
                  v-for="doc in documents"
                  :key="doc.id"
                  :label="doc.name"
                  :name="doc.id"
                >
                  <div class="tab-header">
                    <span class="tab-title">{{ doc.name }}</span>
                    <el-button
                      size="small"
                      type="danger"
                      @click="deleteDocument(doc.id)"
                    >
                      <el-icon><Delete /></el-icon>
                      删除
                    </el-button>
                  </div>
                  <div class="page-grid">
                    <div
                      v-for="(page, index) in doc.pages"
                      :key="index"
                      class="page-item"
                      :class="{ selected: isPageSelected(doc.id, index) }"
                      @click.ctrl.exact="togglePageSelection(doc.id, index)"
                      @click.exact="openPreview(doc.id, index)"
                    >
                      <img :src="page.thumbnail" :alt="`第${index + 1}页`" />
                      <span class="page-number">{{ index + 1 }}</span>
                      <el-icon v-if="isPageSelected(doc.id, index)" class="check-icon">
                        <CircleCheckFilled />
                      </el-icon>
                    </div>
                  </div>
                </el-tab-pane>
              </el-tabs>

              <el-empty v-if="documents.length === 0" description="暂无文档，请先上传" />
            </el-card>
          </el-col>

          <!-- 右侧：拼接队列 -->
          <el-col :span="8">
            <el-card class="merge-queue-card">
              <template #header>
                <span>拼接队列</span>
                <el-tag type="info">{{ queue.length }} 页</el-tag>
              </template>

              <div class="queue-list">
                <div
                  v-for="(page, index) in queue"
                  :key="page.id"
                  class="queue-item"
                >
                  <img :src="page.thumbnail" :alt="`第${index + 1}页`" />
                  <div class="queue-item-info">
                    <span>{{ page.original_document_name }} - 第{{ page.page_index + 1 }}页</span>
                  </div>
                  <el-button
                    size="small"
                    type="danger"
                    circle
                    @click="removeFromQueue(page.id)"
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
                <el-button
                  v-if="mergedFileInfo"
                  type="success"
                  @click="handleDownload"
                >
                  <el-icon><Download /></el-icon>
                  下载合并文档
                </el-button>
              </div>
            </el-card>
          </el-col>
        </el-row>

        <!-- 页面预览对话框 -->
        <el-dialog v-model="showPreviewDialog" title="页面预览" width="800px" class="preview-dialog">
          <div v-if="previewPage" class="preview-content">
            <img :src="previewPage.thumbnail" :alt="`第${previewPage.pageIndex + 1}页`" class="preview-image" />
            <div class="preview-info">
              <p><strong>文档：</strong>{{ previewPage.docName }}</p>
              <p><strong>页码：</strong>第 {{ previewPage.pageIndex + 1 }} 页</p>
              <p><strong>尺寸：</strong>{{ previewPage.width }} × {{ previewPage.height }} px</p>
            </div>
          </div>
          <template #footer>
            <el-button @click="showPreviewDialog = false">关闭</el-button>
            <el-button v-if="previewPage && !isPageSelected(previewPage.docId, previewPage.pageIndex)" type="primary" @click="selectPreviewedPage">
              选择此页面
            </el-button>
            <el-button v-else-if="previewPage" type="warning" @click="deselectPreviewedPage">
              取消选择
            </el-button>
          </template>
        </el-dialog>

        <!-- 合并成功提示 -->
        <el-dialog v-model="showMergeSuccessDialog" title="合并成功" width="400px">
          <div class="merge-success-content">
            <el-icon :size="50" color="#67c23a"><SuccessFilled /></el-icon>
            <p>文档已成功合并！</p>
            <p class="file-info">{{ mergedFileInfo?.filename }}</p>
            <p class="page-info">共 {{ mergedFileInfo?.totalPages }} 页</p>
          </div>
          <template #footer>
            <el-button @click="showMergeSuccessDialog = false">关闭</el-button>
            <el-button type="primary" @click="handleDownload">
              <el-icon><Download /></el-icon>
              下载文件
            </el-button>
          </template>
        </el-dialog>
      </el-main>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ArrowLeft, Plus, Delete, CircleCheckFilled, UploadFilled, Download, SuccessFilled } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useMergeStore } from '@/stores/merge'
import { api } from '@/services/api'
import type { SelectedPage } from '@/stores/merge'
import type { UploadFile } from 'element-plus'

const router = useRouter()
const mergeStore = useMergeStore()
const queue = computed(() => mergeStore.queue)

const activeDocumentId = ref('')
const showUploadDialog = ref(false)
const merging = ref(false)
const uploadFileList = ref<UploadFile[]>([])
const uploading = ref(false)

// 合并成功相关
const showMergeSuccessDialog = ref(false)
const mergedFileInfo = ref<{ filename: string; totalPages: number } | null>(null)

// 页面预览相关
const showPreviewDialog = ref(false)
const previewPage = ref<{ docId: string; docName: string; pageIndex: number; thumbnail: string; width: number; height: number } | null>(null)

// 模拟文档数据
const documents = ref<any[]>([])
const tempUploadFiles = ref<File[]>([])

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
    const selectedPage: SelectedPage = {
      id: pageId,
      document_id: docId,
      page_index: pageIndex,
      original_document_name: doc.name,
      thumbnail: doc.pages[pageIndex].thumbnail,
      page_width: doc.pages[pageIndex].width,
      page_height: doc.pages[pageIndex].height,
      rotation: doc.pages[pageIndex].rotation,
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

async function handleMerge() {
  merging.value = true
  try {
    const config = mergeStore.config
    const result = await api.mergeDocuments(config)
    if (result.success) {
      const filename = result.output_path?.split('/').pop() || 'merged.pdf'
      mergedFileInfo.value = {
        filename,
        totalPages: result.total_pages
      }
      showMergeSuccessDialog.value = true
      ElMessage.success('合并成功！')
    } else {
      ElMessage.error(`合并失败: ${result.error}`)
    }
  } catch (error: any) {
    ElMessage.error(`合并失败: ${error.message}`)
  } finally {
    merging.value = false
  }
}

async function handleDownload() {
  if (!mergedFileInfo.value) {
    ElMessage.warning('请先合并文档')
    return
  }

  try {
    const response = await api.downloadMergedFile(mergedFileInfo.value.filename)
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', mergedFileInfo.value.filename)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  } catch (error: any) {
    ElMessage.error(`下载失败: ${error.message}`)
  }
}

async function deleteDocument(documentId: string) {
  try {
    await ElMessageBox.confirm('确定要删除此文档吗？删除后该文档的所有页面将从队列中移除。', '确认删除', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })

    const result = await api.deleteDocument(documentId)
    if (result.success) {
      documents.value = documents.value.filter(d => d.id !== documentId)
      mergeStore.clearQueue()

      if (activeDocumentId.value === documentId) {
        activeDocumentId.value = documents.value.length > 0 ? documents.value[0].id : ''
      }

      ElMessage.success('文档删除成功')
    } else {
      ElMessage.error(`删除失败: ${result.error}`)
    }
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(`删除失败: ${error.message}`)
    }
  }
}

async function handleFileUpload(file: UploadFile) {
  if (file.raw) {
    tempUploadFiles.value.push(file.raw)
    uploadFileList.value.push(file)
  }
}

async function confirmUpload() {
  if (tempUploadFiles.value.length === 0) {
    ElMessage.warning('请先选择文件')
    return
  }

  uploading.value = true
  try {
    const files = tempUploadFiles.value

    if (files.length === 1) {
      // 单文件上传
      const result = await api.uploadDocument(files[0])

      // 获取文档页面信息
      const pagesResult = await api.getDocumentPages(result.document_id)

      if (pagesResult.success) {
        const docData = {
          id: result.document_id,
          name: result.filename,
          pages: pagesResult.pages.map((p: any, index: number) => ({
            index: p.page_number,
            width: p.width,
            height: p.height,
            rotation: p.rotation,
            thumbnail: p.thumbnail || `data:image/svg+xml;base64,${generatePlaceholderThumbnail(p.width, p.height)}`,
          })),
        }

        documents.value.push(docData)
        activeDocumentId.value = result.document_id
        ElMessage.success('文档上传成功')
      }
    } else {
      // 批量上传
      const result = await api.uploadDocumentsBatch(files)

      const uploadedDocs = result.results.filter((r: any) => r.success)
      const failedDocs = result.results.filter((r: any) => !r.success)

      if (failedDocs.length > 0) {
        ElMessage.warning(`${uploadedDocs.length} 个文件上传成功，${failedDocs.length} 个失败`)
      } else {
        ElMessage.success(`成功上传 ${uploadedDocs.length} 个文档`)
      }

      // 清空队列，因为上传了新文档
      mergeStore.clearQueue()

      // 为每个成功上传的文档获取页面信息
      for (const docResult of uploadedDocs) {
        try {
          const pagesResult = await api.getDocumentPages(docResult.document_id)
          if (pagesResult.success) {
            const docData = {
              id: docResult.document_id,
              name: docResult.filename,
              pages: pagesResult.pages.map((p: any, index: number) => ({
                index: p.page_number,
                width: p.width,
                height: p.height,
                rotation: p.rotation,
                thumbnail: p.thumbnail || `data:image/svg+xml;base64,${generatePlaceholderThumbnail(p.width, p.height)}`,
              })),
            }
            documents.value.push(docData)
            if (!activeDocumentId.value) {
              activeDocumentId.value = docResult.document_id
            }
          }
        } catch (error: any) {
          console.error(`获取文档 ${docResult.filename} 页面信息失败:`, error)
        }
      }
    }

    showUploadDialog.value = false
    uploadFileList.value = []
    tempUploadFiles.value = []
  } catch (error: any) {
    ElMessage.error(`上传文档失败: ${error.message}`)
  } finally {
    uploading.value = false
  }
}

function generatePlaceholderThumbnail(width: number, height: number): string {
  // 生成简单的SVG占位图
  const aspectRatio = width / height
  const svgWidth = 100
  const svgHeight = Math.round(svgWidth / aspectRatio)

  const svg = `<svg width="${svgWidth}" height="${svgHeight}" xmlns="http://www.w3.org/2000/svg">
    <rect width="100%" height="100%" fill="#f0f0f0"/>
    <text x="50%" y="50%" text-anchor="middle" dy=".3em" font-size="12" fill="#999">Page</text>
  </svg>`

  return btoa(svg)
}

// 预览相关方法
function openPreview(docId: string, pageIndex: number) {
  const doc = documents.value.find(d => d.id === docId)
  if (!doc || !doc.pages[pageIndex]) return

  previewPage.value = {
    docId,
    docName: doc.name,
    pageIndex,
    thumbnail: doc.pages[pageIndex].thumbnail,
    width: doc.pages[pageIndex].width || 0,
    height: doc.pages[pageIndex].height || 0,
  }
  showPreviewDialog.value = true
}

async function selectPreviewedPage() {
  if (!previewPage.value) return
  await togglePageSelection(previewPage.value.docId, previewPage.value.pageIndex)
  showPreviewDialog.value = false
}

async function deselectPreviewedPage() {
  if (!previewPage.value) return
  const pageId = `${previewPage.value.docId}_${previewPage.value.pageIndex}`
  await api.deselectPage(pageId)
  mergeStore.removePage(pageId)
  showPreviewDialog.value = false
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

.tab-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  border-bottom: 1px solid #eee;
}

.tab-title {
  flex: 1;
  font-size: 14px;
  font-weight: 500;
}

.el-main {
  padding: 24px;
}

.page-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 16px;
  padding: 16px 0;
}

.page-item {
  position: relative;
  border: 2px solid #eee;
  border-radius: 4px;
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

.page-item img {
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
  font-size: 12px;
}

.check-icon {
  position: absolute;
  top: 4px;
  right: 4px;
  color: #409eff;
  background: white;
  border-radius: 50%;
}

.queue-list {
  max-height: 400px;
  overflow-y: auto;
}

.queue-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px;
  border-bottom: 1px solid #eee;
}

.queue-item img {
  width: 48px;
  height: 68px;
  object-fit: contain;
  border: 1px solid #eee;
}

.queue-item-info {
  flex: 1;
  font-size: 14px;
}

.queue-actions {
  display: flex;
  gap: 8px;
  margin-top: 16px;
}

.queue-actions .el-button {
  flex: 1;
}

.merge-success-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  padding: 20px 0;
}

.merge-success-content .file-info {
  font-weight: bold;
  font-size: 16px;
  color: #303133;
  word-break: break-all;
  text-align: center;
  max-width: 100%;
}

.merge-success-content .page-info {
  color: #909399;
  font-size: 14px;
}

/* 预览对话框样式 */
.preview-dialog :deep(.el-dialog__body) {
  padding: 20px;
}

.preview-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
}

.preview-image {
  max-width: 100%;
  max-height: 500px;
  object-fit: contain;
  border: 1px solid #eee;
  border-radius: 4px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.preview-info {
  width: 100%;
  padding: 12px 16px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.preview-info p {
  margin: 6px 0;
  font-size: 14px;
  color: #606266;
}

/* 页面网格项悬停效果 */
.page-item:hover::after {
  content: '点击预览';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: rgba(0, 0, 0, 0.7);
  color: white;
  padding: 6px 12px;
  border-radius: 4px;
  font-size: 12px;
  pointer-events: none;
}
</style>
