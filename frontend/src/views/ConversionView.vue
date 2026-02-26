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
const selectedFile = ref<File | null>(null)
const converting = ref(false)
const targetFormat = ref('pdf')
const conversionOptions = ref({
  preserve_formatting: true,
  quality: 90,
  dpi: 200,
})

function handleFileChange(file: UploadFile) {
  if (file.raw) {
    selectedFile.value = file.raw
    // 根据文件扩展名设置默认目标格式
    const ext = file.name.split('.').pop()?.toLowerCase()
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

async function handleConvert() {
  if (!selectedFile.value) return

  converting.value = true
  try {
    let result
    const fileExt = selectedFile.value.name.split('.').pop()?.toLowerCase()

    switch (targetFormat.value) {
      case 'pdf':
        // 根据源文件类型选择转换方法
        if (fileExt === 'doc' || fileExt === 'docx') {
          result = await api.wordToPdf(selectedFile.value)
        } else if (fileExt === 'xls' || fileExt === 'xlsx') {
          result = await api.excelToPdf(selectedFile.value)
        } else if (fileExt === 'ppt' || fileExt === 'pptx') {
          result = await api.pptToPdf(selectedFile.value)
        } else {
          result = { success: false, error: '不支持的源格式转换为PDF' }
        }
        break

      case 'word':
        if (fileExt === 'pdf') {
          result = await api.pdfToWord(selectedFile.value)
        } else {
          result = { success: false, error: '只有PDF可以转换为Word' }
        }
        break

      case 'excel':
        if (fileExt === 'pdf') {
          result = await api.pdfToExcel(selectedFile.value)
        } else {
          result = { success: false, error: '只有PDF可以转换为Excel' }
        }
        break

      case 'ppt':
        if (fileExt === 'pdf') {
          result = await api.pdfToPpt(selectedFile.value)
        } else {
          result = { success: false, error: '只有PDF可以转换为PPT' }
        }
        break

      case 'image':
        if (fileExt === 'pdf') {
          result = await api.pdfToImages(selectedFile.value, conversionOptions.value)
        } else {
          result = { success: false, error: '只有PDF可以转换为图片' }
        }
        break

      default:
        result = { success: false, error: '不支持的转换' }
    }

    if (result.success) {
      alert('转换成功！')
    } else {
      alert(`转换失败: ${result.error}`)
    }
  } catch (error: any) {
    alert(`转换失败: ${error.message}`)
  } finally {
    converting.value = false
  }
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
