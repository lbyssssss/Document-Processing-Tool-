<template>
  <div class="conversion-view">
    <el-container>
      <el-header>
        <el-button @click="$router.back()">
          <el-icon><ArrowLeft /></el-icon>
          返回
        </el-button>
        <h2>格式转换</h2>
      </el-header>
      <el-main>
        <el-card class="upload-card">
          <el-upload
            drag
              :auto-upload="false"
              :on-change="handleFileChange"
              :limit="1"
              accept=".pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx,.jpg,.jpeg,.png,.gif,.bmp,.webp"
          >
            <el-icon :size="60"><UploadFilled /></el-icon>
            <div class="el-upload__text">
              将文件拖到此处，或<em>点击上传</em>
            </div>
            <template #tip>
              <div class="el-upload__tip">
                支持 PDF、Word、Excel、PPT、图片格式，最大100MB
              </div>
            </template>
          </el-upload>
        </el-card>
        <el-card v-if="selectedFile" class="options-card">
          <h3>转换选项</h3>
          <el-form :model="conversionOptions" label-width="120px">
            <el-form-item label="目标格式">
              <el-select v-model="targetFormat" placeholder="选择目标格式">
                <el-option label="PDF" value="pdf" />
                <el-option label="Word" value="word" />
                <el-option label="Excel" value="excel" />
                <el-option label="PPT" value="ppt" />
                <el-option label="图片" value="image" />
              </el-select>
            </el-form-item>
            <el-form-item label="保持格式">
              <el-switch v-model="conversionOptions.preserve_formatting" />
            </el-form-item>
            <el-form-item v-if="targetFormat === 'image'" label="输出质量">
              <el-slider v-model="conversionOptions.quality" :min="1" :max="100" />
            </el-form-item>
            <el-form-item v-if="targetFormat === 'image'" label="DPI">
              <el-slider v-model="conversionOptions.dpi" :min="72" :max="300" :step="12" />
            </el-form-item>
          </el-form>
          <el-button type="primary" @click="handleConvert" :loading="converting">
            开始转换
          </el-button>
        </el-card>
      </el-main>
      <el-main>
        <el-alert v-if="errorMessage" type="error" :title="转换错误" :closable="false" show-icon>
          {{ errorMessage }}
        </el-alert>
        <el-alert v-if="successMessage" type="success" :title="转换成功" :closable="false" show-icon>
          {{ successMessage }}
        </el-alert>
        <el-alert v-if="demoMode" type="info" :closable="false" show-icon>
          <template #title>
            <span>演示模式</span>
          </template>
          预览环境中使用模拟数据。实际功能需要在本地运行后端和前端开发服务器。
        </el-alert>
        <el-button type="primary" @click="handleDownload" v-if="outputFileInfo" :loading="downloading">
          下载转换后的文件
        </el-button>
      </el-main>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { UploadFilled, ArrowLeft } from '@element-plus/icons-vue'
import type { UploadFile } from 'element-plus'
import { api } from '@/services/api'

const router = useRouter()
const selectedFile = ref<File | null>(null)
const converting = ref(false)
const downloading = ref(false)
const errorMessage = ref('')
const successMessage = ref('')
const demoMode = ref(false)
const outputFileInfo = ref<any>(null)
const targetFormat = ref('pdf')
const conversionOptions = ref({
  preserve_formatting: true,
  quality: 90,
  dpi: 200,
})

// 演示模式检测 - 预览环境使用外部 API
const isDemoMode = false

function handleFileChange(file: UploadFile) {
  if (file.raw) {
    selectedFile.value = file.raw
  }
}

async function handleConvert() {
  if (!selectedFile.value) return

  converting.value = true
  errorMessage.value = ''
  successMessage.value = ''

  try {
    let result
    const fileExt = selectedFile.value.name.split('.').pop()?.toLowerCase()

    if (isDemoMode) {
      // 演示模式：返回模拟数据
      await new Promise(resolve => setTimeout(resolve, 1500))
      result = {
        success: true,
        output_path: 'demo_output_' + targetFormat.value,
        output_format: targetFormat.value,
        file_size: 1024,
        warnings: ['这是演示模式，实际转换需要在本地运行后端'],
      }
    } else {
      // 实际模式：调用API
      switch (targetFormat.value) {
        case 'pdf':
          if (fileExt === 'doc' || fileExt === 'docx') {
            result = await api.wordToPdf(selectedFile.value)
          } else if (fileExt === 'xls' || fileExt === 'xlsx') {
            result = await api.excelToPdf(selectedFile.value)
          } else if (fileExt === 'ppt' || fileExt === 'pptx') {
            result = await api.pptToPdf(selectedFile.value)
          } else {
            throw new Error('不支持的转换格式')
          }
          break
        case 'word':
          if (fileExt === 'pdf') {
            result = await api.pdfToWord(selectedFile.value)
          } else {
            throw new Error('不支持的转换格式')
          }
          break
        case 'excel':
          if (fileExt === 'pdf') {
            result = await api.pdfToExcel(selectedFile.value)
          } else {
            throw new Error('不支持的转换格式')
          }
          break
        case 'ppt':
          if (fileExt === 'pdf') {
            result = await api.pdfToPpt(selectedFile.value)
          } else {
            throw new Error('不支持的转换格式')
          }
          break
        case 'image':
          if (fileExt === 'pdf') {
            result = await api.pdfToImages(selectedFile.value, conversionOptions.value)
          } else {
            throw new Error('不支持的转换格式')
          }
          break
        default:
          throw new Error('不支持的转换格式')
      }
    }

    if (result.success) {
      successMessage.value = `转换成功！已生成 ${targetFormat.value} 文件`
      outputFileInfo.value = {
        name: selectedFile.value.name,
        size: result.file_size,
        format: result.output_format,
        path: result.output_path,
      }
    } else {
      errorMessage.value = `转换失败：${result.error}`
    }
  } catch (error: any) {
    errorMessage.value = `转换失败：${error.message || error}`
  } finally {
    converting.value = false
  }
}

function handleDownload() {
  if (outputFileInfo.value && isDemoMode) {
    alert('演示模式：这是模拟的文件，实际文件需要后端支持')
  }
}
</script>

<style scoped>
.conversion-view {
  height: 100vh;
}

.el-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  border-bottom: 1px solid #eee;
}

.el-header h1 {
  font-size: 24px;
  font-weight: 600;
}

.nav-menu {
  display: flex;
  gap: 12px;
}

.el-main {
  padding: 24px;
}
</style>
