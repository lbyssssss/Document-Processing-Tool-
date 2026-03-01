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
                <span>上传文档</span>
                <el-upload
                  :auto-upload="true"
                  :show-file-list="false"
                  :on-success="handleUploadSuccess"
                  :on-error="handleUploadError"
                  :before-upload="beforeUpload"
                  accept=".pdf"
                  :action="uploadAction"
                >
                  <el-button size="small" type="primary">
                    <el-icon><Plus /></el-icon>
                    添加文档
                  </el-button>
                </el-upload>
              </template>

              <el-tabs v-model="activeDocumentId">
                <el-tab-pane
                  v-for="doc in documents"
                  :key="doc.id"
                  :label="doc.name"
                  :name="doc.id"
                >
                  <div class="page-grid">
                    <div
                      v-for="(page, index) in doc.pages"
                      :key="index"
                      class="page-item"
                      :class="{ selected: isPageSelected(doc.id, index) }"
                      @click="togglePageSelection(doc.id, index)"
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
              </div>
            </el-card>
          </el-col>
        </el-row>
      </el-main>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ArrowLeft, Plus, Delete, CircleCheckFilled } from '@element-plus/icons-vue'
import { useMergeStore } from '@/stores/merge'
import { api } from '@/services/api'
import { ElMessage } from 'element-plus'
import type { UploadFile, UploadProps } from 'element-plus'
import type { SelectedPage } from '@/stores/merge'

const router = useRouter()
const mergeStore = useMergeStore()
const queue = computed(() => mergeStore.queue)

const activeDocumentId = ref('')
const uploading = ref(false)
const merging = ref(false)
const uploadAction = ref('')

// 模拟文档数据
const documents = ref<any[]>([])

// 设置上传地址
onMounted(() => {
  const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'
  uploadAction.value = `${baseURL}/merge/upload-document`
})

async function handleUploadSuccess(response: any, file: UploadFile) {
  ElMessage.success('文档上传成功')
  const docId = response.document_id
  
  // 加载文档页面
  await loadDocumentPages(docId, file.name)
}

function handleUploadError(error: any) {
  ElMessage.error(`文档上传失败: ${error.message}`)
}

function beforeUpload(file: UploadFile) {
  const isPDF = file.type === 'application/pdf'
  const isLt100M = (file.size || 0) / 1024 / 1024 < 100

  if (!isPDF) {
    ElMessage.error('只能上传PDF文件!')
    return false
  }
  if (!isLt100M) {
    ElMessage.error('文件大小不能超过100MB!')
    return false
  }
  return true
}

async function loadDocumentPages(documentId: string, fileName: string) {
  try {
    const result = await api.getDocumentPages(documentId)
    if (result.success) {
      // 添加到文档列表
      const pages = result.pages.map((page: any) => ({
        page_number: page.page_number,
        width: page.width,
        height: page.height,
        rotation: page.rotation,
        thumbnail: page.thumbnail,
      }))
      
      documents.value.push({
        id: documentId,
        name: fileName || `文档${documentId}`,
        pages: pages,
      })
      
      // 自动激活第一个文档
      if (documents.value.length === 1) {
        activeDocumentId.value = documentId
      }
    }
  } catch (error: any) {
    ElMessage.error(`加载文档页面失败: ${error.message}`)
  }
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
      alert('合并成功！')
    } else {
      alert(`合并失败: ${result.error}`)
    }
  } catch (error: any) {
    alert(`合并失败: ${error.message}`)
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
</style>
