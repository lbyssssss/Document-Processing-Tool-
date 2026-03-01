<template>
  <div class="annotation-view">
    <el-container>
      <el-header>
        <el-button @click="$router.back()">
          <el-icon><ArrowLeft /></el-icon>
          返回
        </el-button>
        <h2>批注管理</h2>
      </el-header>
      <el-main>
        <!-- 文档选择 -->
        <el-card class="document-card">
          <template #header>
            <span>选择文档</span>
          </template>
          <el-select
            v-model="selectedDocumentId"
            placeholder="请选择文档"
            @change="loadAnnotations"
          >
            <el-option
              v-for="doc in documents"
              :key="doc.id"
              :label="doc.name"
              :value="doc.id"
            />
          </el-select>
        </el-card>

        <!-- 批注列表 -->
        <el-card v-if="selectedDocumentId" class="annotations-card">
          <template #header>
            <div class="card-header">
              <span>批注列表</span>
              <el-tag type="info">{{ annotations.length }} 条</el-tag>
            </div>
          </template>

          <div class="annotations-list">
            <div
              v-for="annotation in annotations"
              :key="annotation.id"
              class="annotation-item"
              :class="{ editing: editingId === annotation.id }"
            >
              <div class="annotation-header">
                <span class="annotation-page">第 {{ annotation.page_index + 1 }} 页</span>
                <span class="annotation-author">{{ annotation.author }}</span>
                <span class="annotation-time">{{ formatDate(annotation.created_at) }}</span>
              </div>

              <div class="annotation-content">
                <div v-if="editingId === annotation.id">
                  <el-input
                    v-model="editContent"
                    type="textarea"
                    :rows="3"
                    placeholder="编辑批注内容"
                  />
                  <div class="edit-actions">
                    <el-button size="small" @click="cancelEdit">取消</el-button>
                    <el-button size="small" type="primary" @click="saveEdit(annotation.id)">
                      保存
                    </el-button>
                  </div>
                </div>
                <div v-else>
                  {{ annotation.content }}
                </div>
              </div>

              <div v-if="editingId !== annotation.id" class="annotation-actions">
                <el-button size="small" @click="startEdit(annotation)">
                  编辑
                </el-button>
                <el-button size="small" type="danger" @click="deleteAnnotation(annotation.id)">
                  删除
                </el-button>
              </div>
            </div>

            <el-empty v-if="annotations.length === 0" description="暂无批注" />
          </div>
        </el-card>

        <!-- 添加批注 -->
        <el-card v-if="selectedDocumentId" class="add-annotation-card">
          <h3>添加新批注</h3>
          <el-form :model="newAnnotation" label-width="100px">
            <el-form-item label="页码">
              <el-input-number
                v-model="newAnnotation.page_index"
                :min="1"
                :max="maxPages"
                controls-position="right"
              />
            </el-form-item>
            <el-form-item label="位置X">
              <el-input-number v-model="newAnnotation.position.x" controls-position="right" />
            </el-form-item>
            <el-form-item label="位置Y">
              <el-input-number v-model="newAnnotation.position.y" controls-position="right" />
            </el-form-item>
            <el-form-item label="宽度">
              <el-input-number v-model="newAnnotation.position.width" :min="1" controls-position="right" />
            </el-form-item>
            <el-form-item label="高度">
              <el-input-number v-model="newAnnotation.position.height" :min="1" controls-position="right" />
            </el-form-item>
            <el-form-item label="颜色">
              <el-color-picker v-model="newAnnotation.color" />
            </el-form-item>
            <el-form-item label="内容">
              <el-input
                v-model="newAnnotation.content"
                type="textarea"
                :rows="3"
                placeholder="输入批注内容"
              />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="addAnnotation" :loading="adding">
                添加批注
              </el-button>
              <el-button @click="resetForm">重置</el-button>
            </el-form-item>
          </el-form>
        </el-card>

        <!-- 统计信息 -->
        <el-card v-if="selectedDocumentId" class="stats-card">
          <h3>统计信息</h3>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="文档ID">
              {{ selectedDocumentId }}
            </el-descriptions-item>
            <el-descriptions-item label="批注数量">
              {{ stats.count }}
            </el-descriptions-item>
            <el-descriptions-item label="批注作者">
              {{ stats.authors.join(', ') }}
            </el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-main>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ArrowLeft } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { api } from '@/services/api'

const router = useRouter()

// 文档列表（模拟数据）
const documents = ref([
  { id: 'doc1', name: '文档1.pdf' },
  { id: 'doc2', name: '文档2.pdf' },
  { id: 'doc3', name: '文档3.pdf' },
])

const selectedDocumentId = ref('')
const annotations = ref<any[]>([])
const editingId = ref('')
const editContent = ref('')
const adding = ref(false)
const maxPages = ref(10)

// 新批注表单
const newAnnotation = ref({
  document_id: '',
  page_index: 1,
  position: { x: 100, y: 100, width: 200, height: 100 },
  content: '',
  author: '匿名用户',
  color: '#FF5722',
})

// 统计信息
const stats = computed(() => {
  if (annotations.value.length === 0) {
    return { count: 0, authors: [] }
  }
  return {
    count: annotations.value.length,
    authors: [...new Set(annotations.value.map(a => a.author))],
  }
})

function formatDate(dateString: string) {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN')
}

async function loadAnnotations() {
  if (!selectedDocumentId.value) return

  try {
    newAnnotation.value.document_id = selectedDocumentId.value
    const result = await api.getAnnotations(selectedDocumentId.value)
    annotations.value = result
  } catch (error: any) {
    ElMessage.error(`加载批注失败: ${error.message}`)
  }
}

function startEdit(annotation: any) {
  editingId.value = annotation.id
  editContent.value = annotation.content
}

function cancelEdit() {
  editingId.value = ''
  editContent.value = ''
}

async function saveEdit(annotationId: string) {
  try {
    const annotation = annotations.value.find(a => a.id === annotationId)
    if (!annotation) return

    await api.updateAnnotation(annotationId, {
      ...annotation,
      content: editContent.value,
    })

    annotation.content = editContent.value
    ElMessage.success('批注更新成功')
    cancelEdit()
  } catch (error: any) {
    ElMessage.error(`更新批注失败: ${error.message}`)
  }
}

async function deleteAnnotation(annotationId: string) {
  try {
    await api.deleteAnnotation(annotationId)
    annotations.value = annotations.value.filter(a => a.id !== annotationId)
    ElMessage.success('批注删除成功')
  } catch (error: any) {
    ElMessage.error(`删除批注失败: ${error.message}`)
  }
}

async function addAnnotation() {
  if (!newAnnotation.value.content.trim()) {
    ElMessage.warning('请输入批注内容')
    return
  }

  adding.value = true
  try {
    const result = await api.createAnnotation(newAnnotation.value)
    annotations.value.push(result)
    ElMessage.success('批注添加成功')
    resetForm()
  } catch (error: any) {
    ElMessage.error(`添加批注失败: ${error.message}`)
  } finally {
    adding.value = false
  }
}

function resetForm() {
  newAnnotation.value = {
    document_id: selectedDocumentId.value,
    page_index: 1,
    position: { x: 100, y: 100, width: 200, height: 100 },
    content: '',
    author: '匿名用户',
    color: '#FF5722',
  }
}
</script>

<style scoped>
.annotation-view {
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

.document-card,
.annotations-card,
.add-annotation-card,
.stats-card {
  margin-bottom: 24px;
}

.annotations-card .card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.annotations-list {
  max-height: 500px;
  overflow-y: auto;
}

.annotation-item {
  padding: 16px;
  border: 1px solid #eee;
  border-radius: 8px;
  margin-bottom: 12px;
  transition: all 0.2s;
}

.annotation-item:hover {
  border-color: #409eff;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.1);
}

.annotation-item.editing {
  background-color: #f5f7fa;
}

.annotation-header {
  display: flex;
  gap: 16px;
  margin-bottom: 12px;
  font-size: 14px;
  color: #666;
}

.annotation-page {
  font-weight: 500;
  color: #409eff;
}

.annotation-author {
  flex: 1;
}

.annotation-time {
  font-size: 12px;
}

.annotation-content {
  margin-bottom: 12px;
  line-height: 1.6;
}

.annotation-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

.edit-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  margin-top: 8px;
}

.stats-card h3,
.add-annotation-card h3 {
  margin-bottom: 16px;
}
</style>
