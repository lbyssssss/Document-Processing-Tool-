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
            :limit="10"
            multiple
            :accept="targetFormat === 'image' ? '.jpg,.jpeg,.png,.gif,.bmp,.webp' : '.pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx'"
          >
            <el-icon :size="60"><UploadFilled /></el-icon>
            <div class="el-upload__text">
              将文件拖到此处，或<em>点击上传</em>
            </div>
            <template #tip>
              <div class="el-upload__tip">
                {{ targetFormat === 'image' ? '支持图片格式' : '支持 PDF、Word、Excel、PPT 格式' }}，最大100MB
              </div>
            </template>
          </el-upload>
        </el-card>

        <el-card v-if="selectedFiles.length > 0" class="options-card">
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
            <el-form-item v-if="targetFormat !== 'image'" label="保持格式">
              <el-switch v-model="conversionOptions.preserve_formatting" />
            </el-form-item>
            <el-form-item v-if="targetFormat === 'image'" label="输出格式">
              <el-radio-group v-model="imageOutputFormat">
                <el-radio value="pdf">PDF</el-radio>
                <el-radio value="ppt">PPT</el-radio>
              </el-radio-group>
            </el-form-item>
            <el-form-item v-if="targetFormat === 'image'" label="输出质量">
              <el-slider v-model="conversionOptions.quality" :min="1" :max="100" />
            </el-form-item>
            <el-form-item v-if="targetFormat === 'image' && imageOutputFormat === 'pdf'" label="DPI">
              <el-slider v-model="conversionOptions.dpi" :min="72" :max="300" :step="12" />
            </el-form-item>
          </el-form>
          <el-button type="primary" @click="handleConvert" :loading="converting">
            开始转换 ({{ selectedFiles.length }} 个文件)
          </el-button>
        </el-card>
      </el-main>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { UploadFilled, ArrowLeft } from '@element-plus/icons-vue'
import type { UploadFile } from 'element-plus'
import { api } from '@/services/api'

const router = useRouter()
const selectedFiles = ref<File[]>([])
const converting = ref(false)
const targetFormat = ref('pdf')
const imageOutputFormat = ref('pdf')
const conversionOptions = ref({
  preserve_formatting: true,
  quality: 90,
  dpi: 200,
})

function handleFileChange(file: UploadFile) {
  if (file.raw) {
    selectedFiles.value = [file.raw]
    // 根据文件类型更新目标格式
    const ext = file.name.split('.').pop()?.toLowerCase()
    // 判断是否是图片文件
    if (['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'].includes(`.${ext}`)) {
      // 上传的是图片，设置目标格式为image
      targetFormat.value = 'image'
    } else if (targetFormat.value !== 'image') {
      // 文档上传模式，根据文件扩展名设置默认目标格式
      if (ext === 'pdf') {
        targetFormat.value = 'word'
      } else if (ext === 'doc' || ext === 'docx') {
        targetFormat.value = 'pdf'
      } else if (ext === 'xls' || ext === 'xlsx') {
        targetFormat.value = 'pdf'
      } else if (ext === 'ppt' || ext === 'pptx') {
        targetFormat.value = 'pdf'
      }
    }
  }
}

async function handleConvert() {
  if (selectedFiles.value.length === 0) return

  converting.value = true
  try {
    let result
    const files = selectedFiles.value
    const fileExt = files[0].name.split('.').pop()?.toLowerCase()

    // 根据源格式和目标格式选择转换方法
    if (targetFormat.value === 'image' && isImageFile(files[0].name)) {
      // 图片源，可以转为PDF或PPT
      if (imageOutputFormat.value === 'pdf') {
        result = await api.imagesToPdf(files, conversionOptions.value)
      } else {
        result = await api.imagesToPpt(files)
      }
    } else if (targetFormat.value === 'pdf') {
      // 转为PDF
      if (fileExt === 'doc' || fileExt === 'docx') {
        result = await api.wordToPdf(files[0])
      } else if (fileExt === 'xls' || fileExt === 'xlsx') {
        result = await api.excelToPdf(files[0])
      } else if (fileExt === 'ppt' || fileExt === 'pptx') {
        result = await api.pptToPdf(files[0])
      } else {
        result = { success: false, error: '不支持的源格式转换为PDF' }
      }
    } else if (targetFormat.value === 'word') {
      // 转为Word（仅从PDF）
      if (fileExt === 'pdf') {
        result = await api.pdfToWord(files[0])
      } else {
        result = { success: false, error: '只有PDF可以转换为Word' }
      }
    } else if (targetFormat.value === 'excel') {
      // 转为Excel（仅从PDF）
      if (fileExt === 'pdf') {
        result = await api.pdfToExcel(files[0])
      } else {
        result = { success: false, error: '只有PDF可以转换为Excel' }
      }
    } else if (targetFormat.value === 'ppt') {
      // 转为PPT（仅从PDF）
      if (fileExt === 'pdf') {
        result = await api.pdfToPpt(files[0])
      } else {
        result = { success: false, error: '只有PDF可以转换为PPT' }
      }
    } else {
      result = { success: false, error: '不支持的转换' }
    }

    if (result.success) {
      // 提供下载链接
      if (result.output_path) {
        // 构建下载URL
        const downloadUrl = `/api/v1/conversion/download/${encodeURIComponent(result.output_path)}`
        // 创建下载链接
        const link = document.createElement('a')
        link.href = downloadUrl
        link.download = result.output_path.split('/').pop() || 'converted_file'
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
      }
      alert('转换成功！')
      // 清空选择
      selectedFiles.value = []
    } else {
      alert(`转换失败: ${result.error}`)
    }
  } catch (error: any) {
    alert(`转换失败: ${error.message}`)
  } finally {
    converting.value = false
  }
}

function isImageFile(filename: string): boolean {
  const ext = filename.split('.').pop()?.toLowerCase()
  return ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'].includes(`.${ext}`)
}
</script>

<style scoped>
.conversion-view {
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

.upload-card,
.options-card {
  margin-bottom: 24px;
}

.upload-card .el-icon {
  color: #409eff;
}

.options-card h3 {
  margin-bottom: 16px;
}
</style>
