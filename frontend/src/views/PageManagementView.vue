<template>
  <div class="page-management-view">
    <el-container>
      <el-header>
        <el-button @click="$router.back()">
          <el-icon><ArrowLeft /></el-icon>
          返回
        </el-button>
        <h2>页面管理</h2>
      </el-header>
      <el-main>
        <el-card class="upload-card">
          <el-upload
            drag
            :auto-upload="false"
            :on-change="handleFileChange"
            :limit="1"
            accept=".pdf"
          >
            <el-icon :size="60"><UploadFilled /></el-icon>
            <div class="el-upload__text">
              将PDF文档拖到此处，或<em>点击上传</em>
            </div>
            <template #tip>
              <div class="el-upload__tip">
                支持 PDF 格式，最大100MB
              </div>
            </template>
          </el-upload>
          <el-button
            v-if="selectedFile"
            type="primary"
            @click="handleUpload"
            :loading="uploading"
            style="margin-top: 16px"
          >
            上传并提取页面
          </el-button>
        </el-card>

        <el-card v-if="documentId" class="pages-card">
          <div class="pages-header">
            <h3>页面列表 ({{ pages.length }} 页)</h3>
            <div class="actions">
              <el-button size="small" @click="rotateAllPages(90)">
                <el-icon><RefreshRight /></el-icon>
                全部顺时针旋转
              </el-button>
              <el-button size="small" @click="rotateAllPages(-90)">
                <el-icon><RefreshLeft /></el-icon>
                全部逆时针旋转
              </el-button>
              <el-button type="primary" size="small" @click="exportDocument">
                <el-icon><Download /></el-icon>
                导出文档
              </el-button>
            </div>
          </div>

          <div class="pages-grid">
            <div
              v-for="(page, index) in pages"
              :key="page.id"
              class="page-item"
              :class="{ selected: selectedPageIndex === index }"
              @click="selectPage(index)"
            >
              <div class="page-thumbnail">
                <el-icon :size="60"><Document /></el-icon>
              </div>
              <div class="page-info">
                <span class="page-number">第 {{ page.number }} 页</span>
                <span class="page-size">{{ Math.round(page.width) }} x {{ Math.round(page.height) }}</span>
                <span v-if="page.rotation" class="page-rotation">
                  {{ page.rotation }}°
                </span>
              </div>
              <div class="page-actions">
                <el-button-group>
                  <el-button size="small" @click.stop="rotatePage(page, -90)">
                    <el-icon><RefreshLeft /></el-icon>
                  </el-button>
                  <el-button size="small" @click.stop="rotatePage(page, 90)">
                    <el-icon><RefreshRight /></el-icon>
                  </el-button>
                  <el-button type="danger" size="small" @click.stop="deletePage(page)">
                    <el-icon><Delete /></el-icon>
                  </el-button>
                </el-button-group>
              </div>
            </div>
          </div>
        </el-card>

        <el-drawer
          v-model="pageDetailVisible"
          title="页面详情"
          direction="rtl"
          size="400px"
        >
          <div v-if="selectedPage" class="page-detail">
            <el-form :model="selectedPage" label-width="100px">
              <el-form-item label="页面编号">
                <el-input v-model="selectedPage.number" disabled />
              </el-form-item>
              <el-form-item label="宽度">
                <el-input-number v-model="selectedPage.width" :step="0.1" />
              </el-form-item>
              <el-form-item label="高度">
                <el-input-number v-model="selectedPage.height" :step="0.1" />
              </el-form-item>
              <el-form-item label="旋转角度">
                <el-select v-model="selectedPage.rotation">
                  <el-option label="0°" :value="0" />
                  <el-option label="90°" :value="90" />
                  <el-option label="180°" :value="180" />
                  <el-option label="270°" :value="270" />
                </el-select>
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="savePageDetail">保存修改</el-button>
              </el-form-item>
            </el-form>

            <el-divider />

            <h4>快捷操作</h4>
            <div class="quick-actions">
              <el-button @click="rotatePage(selectedPage, 90)">顺时针旋转 90°</el-button>
              <el-button @click="rotatePage(selectedPage, -90)">逆时针旋转 90°</el-button>
              <el-button @click="rotatePage(selectedPage, 180)">旋转 180°</el-button>
              <el-button type="danger" @click="deletePage(selectedPage)">删除此页</el-button>
            </div>
          </div>
        </el-drawer>
      </el-main>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import {
  UploadFilled,
  ArrowLeft,
  Document,
  RefreshLeft,
  RefreshRight,
  Delete,
  Download,
} from '@element-plus/icons-vue'
import type { UploadFile } from 'element-plus'
import { ElMessage, ElMessageBox } from 'element-plus'

const router = useRouter()
const selectedFile = ref<File | null>(null)
const uploading = ref(false)
const documentId = ref('')
const pages = ref<any[]>([])
const selectedPageIndex = ref<number | null>(null)
const pageDetailVisible = ref(false)

const selectedPage = ref<any>(null)

function handleFileChange(file: UploadFile) {
  if (file.raw) {
    selectedFile.value = file.raw
  }
}

async function handleUpload() {
  if (!selectedFile.value) return

  uploading.value = true

  try {
    const formData = new FormData()
    formData.append('file', selectedFile.value)

    const result = await fetch('/api/v1/page/upload', {
      method: 'POST',
      body: formData,
    }).then(res => res.json())

    if (result.success) {
      documentId.value = result.document_id
      pages.value = result.pages || []
      ElMessage.success(`文档上传成功，共 ${result.total_pages} 页`)
    } else {
      ElMessage.error('文档上传失败')
    }
  } catch (error: any) {
    ElMessage.error(`上传失败：${error.message}`)
  } finally {
    uploading.value = false
  }
}

function selectPage(index: number) {
  selectedPageIndex.value = index
  selectedPage.value = { ...pages.value[index] }
  pageDetailVisible.value = true
}

async function rotatePage(page: any, angle: number) {
  try {
    const result = await fetch(`/api/v1/page/${documentId.value}/pages/${page.id}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        action: 'rotate',
        params: { angle },
      }),
    }).then(res => res.json())

    if (result.success) {
      ElMessage.success('页面旋转成功')
      await refreshPages()
    }
  } catch (error: any) {
    ElMessage.error(`操作失败：${error.message}`)
  }
}

async function rotateAllPages(angle: number) {
  try {
    await ElMessageBox.confirm(
      `确定要${angle > 0 ? '顺时针' : '逆时针'}旋转所有页面吗？`,
      '确认操作',
      { type: 'warning' }
    )

    for (const page of pages.value) {
      await rotatePage(page, angle)
    }

    ElMessage.success('所有页面旋转成功')
  } catch {
    ElMessage.info('已取消操作')
  }
}

async function deletePage(page: any) {
  try {
    await ElMessageBox.confirm(
      `确定要删除第 ${page.number} 页吗？`,
      '确认删除',
      { type: 'warning' }
    )

    const result = await fetch(`/api/v1/page/${documentId.value}/pages/${page.id}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        action: 'delete',
      }),
    }).then(res => res.json())

    if (result.success) {
      ElMessage.success('页面删除成功')
      selectedPage.value = null
      pageDetailVisible.value = false
      await refreshPages()
    }
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(`删除失败：${error.message}`)
    }
  }
}

async function savePageDetail() {
  if (!selectedPage.value) return

  try {
    const result = await fetch(`/api/v1/page/${documentId.value}/pages/${selectedPage.value.id}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        action: 'update',
        params: selectedPage.value,
      }),
    }).then(res => res.json())

    if (result.success) {
      ElMessage.success('保存成功')
      pageDetailVisible.value = false
      await refreshPages()
    }
  } catch (error: any) {
    ElMessage.error(`保存失败：${error.message}`)
  }
}

async function refreshPages() {
  if (!documentId.value) return

  try {
    const result = await fetch(`/api/v1/page/${documentId.value}/pages`)
      .then(res => res.json())

    pages.value = result.pages || []
  } catch (error: any) {
    ElMessage.error(`刷新失败：${error.message}`)
  }
}

function exportDocument() {
  ElMessage.info('导出功能开发中...')
}
</script>

<style scoped>
.page-management-view {
  height: 100vh;
}

.el-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  border-bottom: 1px solid #eee;
}

.el-main {
  padding: 24px;
}

.pages-card {
  margin-top: 24px;
}

.pages-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.pages-header h3 {
  margin: 0;
}

.actions {
  display: flex;
  gap: 8px;
}

.pages-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
}

.page-item {
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  padding: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.page-item:hover {
  border-color: #409eff;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.2);
}

.page-item.selected {
  border-color: #409eff;
  background-color: #ecf5ff;
}

.page-thumbnail {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 200px;
  background-color: #f5f5f5;
  border-radius: 4px;
  color: #999;
}

.page-info {
  margin-top: 12px;
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-size: 14px;
}

.page-number {
  font-weight: 600;
}

.page-size {
  color: #666;
  font-size: 12px;
}

.page-rotation {
  color: #409eff;
  font-size: 12px;
}

.page-actions {
  margin-top: 8px;
}

.quick-actions {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
</style>
