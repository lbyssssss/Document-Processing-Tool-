<template>
  <div class="annotation-view">
    <el-container>
      <el-header>
        <el-button @click="$router.back()">
          <el-icon><ArrowLeft /></el-icon>
          返回
        </el-button>
        <h2>批注编辑</h2>
      </el-header>
      <el-main>
        <el-card class="upload-card">
          <el-input
            v-model="documentId"
            placeholder="输入文档 ID"
            style="margin-bottom: 16px"
          />
          <el-button
            type="primary"
            @click="loadAnnotations"
            :loading="loading"
          >
            加载批注
          </el-button>
        </el-card>

        <el-card v-if="documentId" class="editor-card">
          <div class="toolbar">
            <h3>批注工具</h3>
            <el-radio-group v-model="currentAnnotation.type">
              <el-radio-button label="text">文本</el-radio-button>
              <el-radio-button label="highlight">高亮</el-radio-button>
              <el-radio-button label="freehand">手绘</el-radio-button>
              <el-radio-button label="shape">形状</el-radio-button>
            </el-radio-group>
            <el-color-picker v-model="currentAnnotation.color" />
          </div>

          <div
            class="canvas-area"
            @click="handleCanvasClick"
            @mousemove="handleMouseMove"
          >
            <div class="page-placeholder">
              <el-icon :size="100"><Document /></el-icon>
              <p>点击此处添加批注</p>
              <p class="hint">({{ mousePos.x }}, {{ mousePos.y }})</p>
            </div>

            <div
              v-for="annotation in annotations"
              :key="annotation.id"
              class="annotation-mark"
              :style="getAnnotationStyle(annotation)"
              @click.stop="selectAnnotation(annotation)"
            >
              <span v-if="annotation.type === 'text'" class="text-annotation">
                {{ annotation.content }}
              </span>
              <span v-else-if="annotation.type === 'highlight'" class="highlight-annotation">
                {{ annotation.content }}
              </span>
              <span v-else class="shape-annotation" />
            </div>
          </div>

          <div v-if="selectedAnnotation" class="annotation-detail">
            <el-form :model="selectedAnnotation" label-width="80px">
              <el-form-item label="内容">
                <el-input v-model="selectedAnnotation.content" />
              </el-form-item>
              <el-form-item label="页面">
                <el-input-number v-model="selectedAnnotation.page" :min="1" />
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="saveAnnotation">保存</el-button>
                <el-button type="danger" @click="deleteAnnotation">删除</el-button>
              </el-form-item>
            </el-form>
          </div>

          <div v-else class="new-annotation-form">
            <el-form :model="currentAnnotation" label-width="80px">
              <el-form-item label="内容">
                <el-input
                  v-model="currentAnnotation.content"
                  placeholder="输入批注内容"
                />
              </el-form-item>
              <el-form-item label="页面">
                <el-input-number v-model="currentAnnotation.page" :min="1" />
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="addAnnotation">添加批注</el-button>
              </el-form-item>
            </el-form>
          </div>

          <div class="annotations-list">
            <h4>所有批注 ({{ annotations.length }})</h4>
            <el-table :data="annotations" style="width: 100%">
              <el-table-column prop="page" label="页面" width="80" />
              <el-table-column prop="type" label="类型" width="100">
                <template #default="{ row }">
                  <el-tag :type="getTypeTagType(row.type)">
                    {{ getTypeLabel(row.type) }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="content" label="内容" />
              <el-table-column prop="created_at" label="创建时间" width="180" />
              <el-table-column label="操作" width="100">
                <template #default="{ row }">
                  <el-button
                    type="danger"
                    size="small"
                    @click="deleteAnnotationById(row.id)"
                  >
                    删除
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-card>
      </el-main>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ArrowLeft, Document } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const router = useRouter()
const documentId = ref('')
const loading = ref(false)
const annotations = ref<any[]>([])
const selectedAnnotation = ref<any>(null)
const mousePos = ref({ x: 0, y: 0 })

const currentAnnotation = ref({
  type: 'text',
  content: '',
  color: '#ff0000',
  page: 1,
  x: 0,
  y: 0,
  width: 100,
  height: 30,
})

async function loadAnnotations() {
  if (!documentId.value) {
    ElMessage.warning('请输入文档 ID')
    return
  }

  loading.value = true

  try {
    const result = await fetch(`/api/v1/annotation/${documentId.value}`)
      .then(res => res.json())

    annotations.value = result.annotations || []
  } catch (error: any) {
    ElMessage.error(`加载批注失败：${error.message}`)
  } finally {
    loading.value = false
  }
}

function handleCanvasClick(event: MouseEvent) {
  const rect = (event.currentTarget as HTMLElement).getBoundingClientRect()
  currentAnnotation.value.x = event.clientX - rect.left
  currentAnnotation.value.y = event.clientY - rect.top
}

function handleMouseMove(event: MouseEvent) {
  const rect = (event.currentTarget as HTMLElement).getBoundingClientRect()
  mousePos.value.x = Math.round(event.clientX - rect.left)
  mousePos.value.y = Math.round(event.clientY - rect.top)
}

async function addAnnotation() {
  if (!documentId.value || !currentAnnotation.value.content) {
    ElMessage.warning('请填写完整信息')
    return
  }

  try {
    const now = new Date().toISOString()

    const result = await fetch(`/api/v1/annotation/${documentId.value}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        ...currentAnnotation.value,
        id: '',
        created_at: now,
      }),
    }).then(res => res.json())

    if (result.success) {
      ElMessage.success('批注添加成功')
      await loadAnnotations()
      currentAnnotation.value.content = ''
    }
  } catch (error: any) {
    ElMessage.error(`添加批注失败：${error.message}`)
  }
}

function selectAnnotation(annotation: any) {
  selectedAnnotation.value = { ...annotation }
}

async function saveAnnotation() {
  if (!selectedAnnotation.value) return

  try {
    await fetch(`/api/v1/annotation/${documentId.value}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(selectedAnnotation.value),
    }).then(res => res.json())

    ElMessage.success('批注保存成功')
    selectedAnnotation.value = null
    await loadAnnotations()
  } catch (error: any) {
    ElMessage.error(`保存批注失败：${error.message}`)
  }
}

async function deleteAnnotationById(id: string) {
  try {
    const result = await fetch(`/api/v1/annotation/${documentId.value}/${id}`, {
      method: 'DELETE',
    }).then(res => res.json())

    if (result.success) {
      ElMessage.success('批注删除成功')
      await loadAnnotations()
    }
  } catch (error: any) {
    ElMessage.error(`删除批注失败：${error.message}`)
  }
}

async function deleteAnnotation() {
  if (!selectedAnnotation.value) return

  await deleteAnnotationById(selectedAnnotation.value.id)
  selectedAnnotation.value = null
}

function getAnnotationStyle(annotation: any) {
  return {
    position: 'absolute',
    left: annotation.x + 'px',
    top: annotation.y + 'px',
    width: annotation.width + 'px',
    height: annotation.height + 'px',
    backgroundColor: annotation.type === 'highlight' ? annotation.color + '40' : 'transparent',
    border: annotation.type === 'shape' ? `2px solid ${annotation.color}` : 'none',
  }
}

function getTypeLabel(type: string): string {
  const labels: Record<string, string> = {
    text: '文本',
    highlight: '高亮',
    freehand: '手绘',
    shape: '形状',
  }
  return labels[type] || type
}

function getTypeTagType(type: string): any {
  const types: Record<string, string> = {
    text: 'primary',
    highlight: 'warning',
    freehand: 'success',
    shape: 'info',
  }
  return types[type] || ''
}
</script>

<style scoped>
.annotation-view {
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

.editor-card {
  margin-top: 24px;
}

.toolbar {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid #eee;
}

.canvas-area {
  position: relative;
  width: 100%;
  height: 400px;
  background-color: #f5f5f5;
  border: 1px dashed #d9d9d9;
  border-radius: 4px;
  overflow: hidden;
}

.page-placeholder {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
  color: #999;
}

.page-placeholder p {
  margin: 8px 0;
}

.hint {
  font-size: 12px;
  color: #bbb;
}

.annotation-mark {
  position: absolute;
  cursor: pointer;
  transition: all 0.2s;
}

.annotation-mark:hover {
  box-shadow: 0 0 8px rgba(0, 0, 0, 0.2);
  z-index: 10;
}

.text-annotation {
  display: inline-block;
  padding: 4px 8px;
  background-color: rgba(255, 255, 255, 0.9);
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  font-size: 12px;
  color: #333;
}

.highlight-annotation {
  background-color: rgba(255, 255, 0, 0.5);
  padding: 2px 4px;
  font-size: 12px;
  color: #333;
}

.shape-annotation {
  display: block;
}

.annotation-detail,
.new-annotation-form {
  margin-top: 24px;
  padding: 16px;
  background-color: #f9f9f9;
  border-radius: 4px;
}

.annotations-list {
  margin-top: 24px;
}
</style>
