<template>
  <div class="batch-view">
    <el-container>
      <el-header>
        <el-button @click="$router.back()">
          <el-icon><ArrowLeft /></el-icon>
          返回
        </el-button>
        <h2>批量处理</h2>
      </el-header>
      <el-main>
        <!-- 任务类型选择 -->
        <el-card class="task-type-card">
          <h3>选择处理类型</h3>
          <el-radio-group v-model="taskType" @change="handleTypeChange">
            <el-radio-button label="convert">批量转换</el-radio-button>
            <el-radio-button label="images_to_pdf">图片转PDF</el-radio-button>
          </el-radio-group>
        </el-card>

        <!-- 文件上传 -->
        <el-card class="upload-card">
          <template #header>
            <div class="upload-header">
              <span>上传文件</span>
              <el-tag type="info">{{ uploadedFiles.length }} 个文件</el-tag>
            </div>
          </template>
          <el-upload
            drag
            :auto-upload="false"
            :on-change="handleFileChange"
            :on-remove="handleFileRemove"
            :file-list="fileList"
            multiple
            :accept="acceptTypes"
          >
            <el-icon :size="60"><UploadFilled /></el-icon>
            <div class="el-upload__text">
              将文件拖到此处，或<em>点击上传</em>
            </div>
            <template #tip>
              <div class="el-upload__tip">
                {{ acceptTip }}
              </div>
            </template>
          </el-upload>
        </el-card>

        <!-- 转换选项 -->
        <el-card v-if="taskType === 'convert'" class="options-card">
          <h3>转换选项</h3>
          <el-form :model="convertOptions" label-width="120px">
            <el-form-item label="目标格式">
              <el-select v-model="convertOptions.target_format" placeholder="选择目标格式">
                <el-option label="PDF" value="pdf" />
                <el-option label="Word" value="docx" />
                <el-option label="Excel" value="xlsx" />
                <el-option label="PPT" value="pptx" />
              </el-select>
            </el-form-item>
            <el-form-item label="保持格式">
              <el-switch v-model="convertOptions.preserve_formatting" />
            </el-form-item>
            <el-form-item label="输出质量">
              <el-slider
                v-model="convertOptions.quality"
                :min="1"
                :max="100"
                show-input
              />
            </el-form-item>
            <el-form-item label="DPI (PDF转图片)">
              <el-input-number
                v-model="convertOptions.dpi"
                :min="72"
                :max="300"
                :step="12"
                controls-position="right"
              />
            </el-form-item>
          </el-form>
        </el-card>

        <!-- 图片转PDF选项 -->
        <el-card v-if="taskType === 'images_to_pdf'" class="options-card">
          <h3>PDF选项</h3>
          <el-form :model="pdfOptions" label-width="120px">
            <el-form-item label="页面尺寸">
              <el-select v-model="pdfOptions.page_size">
                <el-option label="A4" value="a4" />
                <el-option label="A3" value="a3" />
                <el-option label="Letter" value="letter" />
                <el-option label="自动" value="auto" />
              </el-select>
            </el-form-item>
            <el-form-item label="页面方向">
              <el-select v-model="pdfOptions.orientation">
                <el-option label="保持原样" value="keep-original" />
                <el-option label="纵向" value="portrait" />
                <el-option label="横向" value="landscape" />
              </el-select>
            </el-form-item>
            <el-form-item label="每批处理">
              <el-input-number
                v-model="pdfOptions.batch_size"
                :min="1"
                :max="50"
                controls-position="right"
              />
            </el-form-item>
          </el-form>
        </el-card>

        <!-- 开始处理按钮 -->
        <el-card class="action-card">
          <el-button
            type="primary"
            size="large"
            @click="startBatch"
            :disabled="uploadedFiles.length === 0 || processing"
            :loading="processing"
          >
            <el-icon><VideoPlay /></el-icon>
            开始批量处理
          </el-button>
        </el-card>

        <!-- 任务状态 -->
        <el-card v-if="currentTask" class="status-card">
          <template #header>
            <div class="status-header">
              <span>任务状态</span>
              <el-tag :type="getStatusType(currentTask.status)">
                {{ getStatusText(currentTask.status) }}
              </el-tag>
            </div>
          </template>

          <!-- 进度条 -->
          <div v-if="currentTask.status === 'running'" class="progress-section">
            <div class="progress-info">
              <span>处理进度: {{ currentTask.current_index }} / {{ currentTask.total_count }}</span>
              <span>{{ Math.round(currentTask.progress) }}%</span>
            </div>
            <el-progress :percentage="currentTask.progress" :status="getProgressStatus(currentTask)" />
          </div>

          <!-- 完成状态 -->
          <div v-if="currentTask.status === 'completed'" class="result-section">
            <el-result
              icon="success"
              title="处理完成"
              :sub-title="`成功: ${currentTask.success_count} 个, 失败: ${currentTask.failure_count} 个`"
            />
            <el-button type="primary" @click="showResultDetails">查看详情</el-button>
          </div>

          <!-- 失败状态 -->
          <div v-if="currentTask.status === 'failed'" class="error-section">
            <el-result icon="error" title="处理失败" :sub-title="currentTask.error_message || '未知错误'" />
            <el-button @click="resetTask">重新开始</el-button>
          </div>

          <!-- 任务信息 -->
          <div class="task-info">
            <el-descriptions :column="2" border>
              <el-descriptions-item label="任务ID">
                {{ currentTask.task_id }}
              </el-descriptions-item>
              <el-descriptions-item label="总文件数">
                {{ currentTask.total_count }}
              </el-descriptions-item>
              <el-descriptions-item label="开始时间">
                {{ formatDate(currentTask.started_at) }}
              </el-descriptions-item>
              <el-descriptions-item label="完成时间">
                {{ formatDate(currentTask.completed_at) }}
              </el-descriptions-item>
            </el-descriptions>
          </div>
        </el-card>

        <!-- 任务列表 -->
        <el-card class="tasks-list-card">
          <template #header>
            <div class="tasks-header">
              <span>历史任务</span>
              <el-button size="small" @click="loadTasks">
                <el-icon><Refresh /></el-icon>
                刷新
              </el-button>
            </div>
          </template>
          <el-table :data="taskList" max-height="300">
            <el-table-column prop="task_id" label="任务ID" width="180" />
            <el-table-column prop="total_count" label="文件数" width="80" />
            <el-table-column label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)" size="small">
                  {{ getStatusText(row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="进度" width="120">
              <template #default="{ row }">
                <el-progress
                  v-if="row.status === 'running'"
                  :percentage="Math.round(row.progress)"
                  :status="getProgressStatus(row)"
                />
                <span v-else>-</span>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="150">
              <template #default="{ row }">
                <el-button size="small" @click="viewTask(row.task_id)">
                  查看
                </el-button>
                <el-button
                  v-if="row.status === 'running'"
                  size="small"
                  type="danger"
                  @click="cancelTask(row.task_id)"
                >
                  取消
                </el-button>
              </template>
            </el-table-column>
          </el-table>
          <el-empty v-if="taskList.length === 0" description="暂无历史任务" />
        </el-card>
      </el-main>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  ArrowLeft,
  UploadFilled,
  VideoPlay,
  Refresh,
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { api } from '@/services/api'
import type { UploadUserFile, UploadFile } from 'element-plus'

const router = useRouter()

// 任务类型
const taskType = ref('convert')

// 文件列表
const fileList = ref<UploadFile[]>([])
const uploadedFiles = ref<File[]>([])
const processing = ref(false)
const currentTask = ref<any>(null)
const taskList = ref<any[]>([])

// 转换选项
const convertOptions = ref({
  target_format: 'pdf',
  preserve_formatting: true,
  quality: 90,
  dpi: 200,
})

// PDF选项
const pdfOptions = ref({
  page_size: 'a4',
  orientation: 'keep-original',
  batch_size: 10,
})

// 计算属性
const acceptTypes = computed(() => {
  if (taskType.value === 'convert') {
    return '.pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx'
  } else if (taskType.value === 'images_to_pdf') {
    return '.jpg,.jpeg,.png,.gif,.bmp,.webp'
  }
  return '*'
})

const acceptTip = computed(() => {
  if (taskType.value === 'convert') {
    return '支持 PDF、Word、Excel、PPT 格式'
  } else if (taskType.value === 'images_to_pdf') {
    return '支持 JPG、PNG、GIF、BMP、WebP 格式'
  }
  return ''
})

function handleTypeChange() {
  // 清空文件列表
  fileList.value = []
  uploadedFiles.value = []
}

function handleFileChange(file: UploadFile) {
  if (file.raw) {
    uploadedFiles.value.push(file.raw)
  }
}

function handleFileRemove(file: UploadFile) {
  uploadedFiles.value = uploadedFiles.value.filter(f => f.name !== file.name)
}

async function startBatch() {
  if (uploadedFiles.value.length === 0) {
    ElMessage.warning('请先上传文件')
    return
  }

  processing.value = true

  try {
    let result
    if (taskType.value === 'convert') {
      result = await api.batchConvert(uploadedFiles.value, {
        task_type: 'convert',
        target_format: convertOptions.value.target_format,
        preserve_formatting: convertOptions.value.preserve_formatting,
        quality: convertOptions.value.quality,
        dpi: convertOptions.value.dpi,
      })
    } else if (taskType.value === 'images_to_pdf') {
      result = await api.batchImagesToPdf(uploadedFiles.value, {
        task_type: 'images_to_pdf',
        page_size: pdfOptions.value.page_size,
        orientation: pdfOptions.value.orientation,
        batch_size: pdfOptions.value.batch_size,
      })
    }

    currentTask.value = {
      task_id: result.task_id,
      status: 'running',
      total_count: result.total_files,
      current_index: 0,
      progress: 0,
      success_count: 0,
      failure_count: 0,
    }

    ElMessage.success('批量处理任务已创建')

    // 轮询任务状态
    pollTaskStatus(result.task_id)
  } catch (error: any) {
    ElMessage.error(`启动批量处理失败: ${error.message}`)
  } finally {
    processing.value = false
  }
}

async function pollTaskStatus(taskId: string) {
  const interval = setInterval(async () => {
    try {
      const status = await api.getBatchStatus(taskId)
      currentTask.value = status

      if (status.status === 'completed' || status.status === 'failed' || status.status === 'cancelled') {
        clearInterval(interval)
        await loadTasks()
      }
    } catch (error: any) {
      console.error('获取任务状态失败:', error)
    }
  }, 2000)
}

async function loadTasks() {
  try {
    const tasks = await api.listBatchTasks()
    taskList.value = tasks.reverse()  // 最新的任务在前
  } catch (error: any) {
    console.error('加载任务列表失败:', error)
  }
}

async function cancelTask(taskId: string) {
  try {
    await api.cancelBatchTask(taskId)
    ElMessage.success('任务已取消')
    await loadTasks()
  } catch (error: any) {
    ElMessage.error(`取消任务失败: ${error.message}`)
  }
}

function viewTask(taskId: string) {
  const task = taskList.value.find(t => t.task_id === taskId)
  if (task) {
    currentTask.value = task
  }
}

function resetTask() {
  currentTask.value = null
  fileList.value = []
  uploadedFiles.value = []
}

function showResultDetails() {
  // 显示结果详情对话框（这里简化处理）
  ElMessage.info('请查看任务历史记录中的详细信息')
}

function getStatusType(status: string) {
  const statusMap: Record<string, any> = {
    pending: 'info',
    running: 'warning',
    completed: 'success',
    failed: 'danger',
    cancelled: 'info',
  }
  return statusMap[status] || 'info'
}

function getStatusText(status: string) {
  const textMap: Record<string, string> = {
    pending: '等待中',
    running: '处理中',
    completed: '已完成',
    failed: '失败',
    cancelled: '已取消',
  }
  return textMap[status] || status
}

function getProgressStatus(task: any) {
  if (task.failure_count > 0) {
    return 'exception'
  }
  return undefined
}

function formatDate(dateString: string) {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN')
}

onMounted(() => {
  loadTasks()
})
</script>

<style scoped>
.batch-view {
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

.task-type-card,
.upload-card,
.options-card,
.action-card,
.status-card,
.tasks-list-card {
  margin-bottom: 24px;
}

.task-type-card h3,
.options-card h3 {
  margin-bottom: 16px;
}

.upload-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.upload-card .el-icon {
  color: #409eff;
}

.action-card {
  text-align: center;
}

.action-card .el-button {
  min-width: 200px;
}

.status-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.progress-section {
  padding: 20px 0;
}

.progress-info {
  display: flex;
  justify-content: space-between;
  margin-bottom: 16px;
  font-size: 16px;
}

.result-section,
.error-section {
  padding: 20px 0;
}

.task-info {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #eee;
}

.tasks-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
