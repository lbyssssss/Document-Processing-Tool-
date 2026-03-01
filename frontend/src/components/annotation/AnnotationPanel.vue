<template>
  <div class="annotation-panel">
    <div class="panel-header">
      <h3>批注管理</h3>
      <el-button size="small" type="primary" @click="showAddDialog = true">
        <el-icon><Plus /></el-icon>
        添加批注
      </el-button>
    </div>

    <div class="panel-content">
      <el-empty v-if="annotations.length === 0" description="暂无批注" />

      <div v-else class="annotation-list">
        <div
          v-for="annotation in annotations"
          :key="annotation.id"
          class="annotation-item"
          @click="selectAnnotation(annotation)"
        >
          <div class="annotation-header">
            <span class="page-tag">第{{ annotation.page_index + 1 }}页</span>
            <span class="author">{{ annotation.author }}</span>
            <span class="time">{{ formatTime(annotation.created_at) }}</span>
          </div>
          <div class="annotation-body">
            <p>{{ annotation.content }}</p>
          </div>
          <div class="annotation-actions">
            <el-button size="small" type="primary" text @click.stop="editAnnotation(annotation)">
              编辑
            </el-button>
            <el-button size="small" type="danger" text @click.stop="deleteAnnotation(annotation.id)">
              删除
            </el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- 添加批注对话框 -->
    <el-dialog
      v-model="showAddDialog"
      title="添加批注"
      width="500px"
      :before-close="handleDialogClose"
    >
      <el-form :model="annotationForm" label-width="80px">
        <el-form-item label="页码">
          <el-input-number v-model="annotationForm.page_index" :min="1" />
        </el-form-item>
        <el-form-item label="位置X">
          <el-input-number v-model="annotationForm.position.x" :min="0" />
        </el-form-item>
        <el-form-item label="位置Y">
          <el-input-number v-model="annotationForm.position.y" :min="0" />
        </el-form-item>
        <el-form-item label="宽度">
          <el-input-number v-model="annotationForm.position.width" :min="1" />
        </el-form-item>
        <el-form-item label="高度">
          <el-input-number v-model="annotationForm.position.height" :min="1" />
        </el-form-item>
        <el-form-item label="作者">
          <el-input v-model="annotationForm.author" placeholder="请输入作者名称" />
        </el-form-item>
        <el-form-item label="颜色">
          <el-color-picker v-model="annotationForm.color" />
        </el-form-item>
        <el-form-item label="内容">
          <el-input
            v-model="annotationForm.content"
            type="textarea"
            :rows="4"
            placeholder="请输入批注内容"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="handleDialogClose">取消</el-button>
        <el-button type="primary" @click="saveAnnotation">保存</el-button>
      </template>
    </el-dialog>

    <!-- 编辑批注对话框 -->
    <el-dialog
      v-model="showEditDialog"
      title="编辑批注"
      width="500px"
      :before-close="handleEditDialogClose"
    >
      <el-form :model="editingAnnotation" label-width="80px">
        <el-form-item label="内容">
          <el-input
            v-model="editingAnnotation.content"
            type="textarea"
            :rows="4"
            placeholder="请输入批注内容"
          />
        </el-form-item>
        <el-form-item label="颜色">
          <el-color-picker v-model="editingAnnotation.color" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="handleEditDialogClose">取消</el-button>
        <el-button type="primary" @click="updateAnnotation">更新</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { api } from '@/services/api'
import { ElMessage, ElMessageBox } from 'element-plus'

interface Rectangle {
  x: number
  y: number
  width: number
  height: number
}

interface Annotation {
  id: string
  document_id: string
  page_index: number
  position: Rectangle
  content: string
  author: string
  color: string
  created_at?: string
  updated_at?: string
}

interface Props {
  documentId: string
}

const props = defineProps<Props>()

const annotations = ref<Annotation[]>([])
const showAddDialog = ref(false)
const showEditDialog = ref(false)
const editingAnnotation = ref<Annotation>({
  id: '',
  document_id: props.documentId,
  page_index: 1,
  position: { x: 0, y: 0, width: 100, height: 50 },
  content: '',
  author: 'anonymous',
  color: '#FF5722',
})

const annotationForm = ref({
  document_id: props.documentId,
  page_index: 1,
  position: { x: 0, y: 0, width: 100, height: 50 },
  content: '',
  author: 'anonymous',
  color: '#FF5722',
})

async function loadAnnotations() {
  try {
    const result = await api.getAnnotations(props.documentId)
    if (result.success) {
      annotations.value = result.annotations
    }
  } catch (error: any) {
    ElMessage.error(`加载批注失败: ${error.message}`)
  }
}

function formatTime(timeStr?: string) {
  if (!timeStr) return ''
  const date = new Date(timeStr)
  return date.toLocaleString('zh-CN')
}

function handleDialogClose() {
  showAddDialog.value = false
  resetForm()
}

function handleEditDialogClose() {
  showEditDialog.value = false
}

function resetForm() {
  annotationForm.value = {
    document_id: props.documentId,
    page_index: 1,
    position: { x: 0, y: 0, width: 100, height: 50 },
    content: '',
    author: 'anonymous',
    color: '#FF5722',
  }
}

async function saveAnnotation() {
  if (!annotationForm.value.content.trim()) {
    ElMessage.warning('请输入批注内容')
    return
  }

  try {
    await api.createAnnotation(annotationForm.value)
    ElMessage.success('批注添加成功')
    showAddDialog.value = false
    resetForm()
    await loadAnnotations()
  } catch (error: any) {
    ElMessage.error(`添加批注失败: ${error.message}`)
  }
}

function editAnnotation(annotation: Annotation) {
  editingAnnotation.value = { ...annotation }
  showEditDialog.value = true
}

async function updateAnnotation() {
  if (!editingAnnotation.value.content.trim()) {
    ElMessage.warning('请输入批注内容')
    return
  }

  try {
    await api.updateAnnotation(editingAnnotation.value.id, props.documentId, editingAnnotation.value)
    ElMessage.success('批注更新成功')
    showEditDialog.value = false
    await loadAnnotations()
  } catch (error: any) {
    ElMessage.error(`更新批注失败: ${error.message}`)
  }
}

async function deleteAnnotation(annotationId: string) {
  try {
    await ElMessageBox.confirm('确定要删除该批注吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })

    await api.deleteAnnotation(annotationId, props.documentId)
    ElMessage.success('批注删除成功')
    await loadAnnotations()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(`删除批注失败: ${error.message}`)
    }
  }
}

function selectAnnotation(annotation: Annotation) {
  // 触发自定义事件，让父组件知道选中的批注
  // 可以用于在PDF预览中高亮显示批注位置
}

onMounted(() => {
  loadAnnotations()
})

// 监听documentId变化
watch(() => props.documentId, () => {
  if (props.documentId) {
    loadAnnotations()
  }
})
</script>

<style scoped>
.annotation-panel {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid #eee;
}

.panel-header h3 {
  margin: 0;
}

.panel-content {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

.annotation-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.annotation-item {
  border: 1px solid #eee;
  border-radius: 8px;
  padding: 12px;
  cursor: pointer;
  transition: all 0.2s;
  background: white;
}

.annotation-item:hover {
  border-color: #409eff;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.1);
}

.annotation-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  font-size: 12px;
}

.page-tag {
  background: #409eff;
  color: white;
  padding: 2px 6px;
  border-radius: 4px;
  font-weight: bold;
}

.author {
  color: #606266;
}

.time {
  margin-left: auto;
  color: #909399;
}

.annotation-body {
  margin: 8px 0;
}

.annotation-body p {
  margin: 0;
  color: #303133;
  line-height: 1.6;
}

.annotation-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  margin-top: 8px;
}
</style>
