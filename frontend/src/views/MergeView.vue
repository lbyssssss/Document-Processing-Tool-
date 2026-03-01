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
            :limit="1"
          >
            <el-icon :size="60"><UploadFilled /></el-icon>
            <div class="el-upload__text">
              将PDF文件拖到此处，或<em>点击上传</em>
            </div>
            <template #tip>
              <div class="el-upload__tip">
                只支持PDF格式
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
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ArrowLeft, Plus, Delete, CircleCheckFilled, UploadFilled } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
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

// 模拟文档数据
const documents = ref<any[]>([])
const tempUploadFile = ref<File | null>(null)

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

async function handleFileUpload(file: UploadFile) {
  if (file.raw) {
    tempUploadFile.value = file.raw
    uploadFileList.value = [file]
  }
}

async function confirmUpload() {
  if (!tempUploadFile.value) {
    ElMessage.warning('请先选择文件')
    return
  }

  uploading.value = true
  try {
    // 上传文件到后端
    const result = await api.uploadDocument(tempUploadFile.value)

    // 获取文档页面信息
    const pagesResult = await api.getDocumentPages(result.document_id)

    if (pagesResult.success) {
      // 生成页面缩略图数据（使用占位图）
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
      showUploadDialog.value = false
      uploadFileList.value = []
      tempUploadFile.value = null
      ElMessage.success('文档上传成功')
    }
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
