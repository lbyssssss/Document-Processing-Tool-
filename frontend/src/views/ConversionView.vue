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
            <el-form-item label="输出质量">
              <el-slider v-model="conversionOptions.quality" :min="1" :max="100" />
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
})

function handleFileChange(file: UploadFile) {
  if (file.raw) {
    selectedFile.value = file.raw
  }
}

async function handleConvert() {
  if (!selectedFile.value) return

  converting.value = true
  try {
    let result
    switch (targetFormat.value) {
      case 'pdf':
        result = await api.wordToPdf(selectedFile.value)
        break
      case 'word':
        result = await api.pdfToWord(selectedFile.value)
        break
      // 添加其他格式转换
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
