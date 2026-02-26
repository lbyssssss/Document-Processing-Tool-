<template>
  <div class="search-view">
    <el-container>
      <el-header>
        <el-button @click="$router.back()">
          <el-icon><ArrowLeft /></el-icon>
          返回
        </el-button>
        <h2>全文检索</h2>
      </el-header>
      <el-main>
        <el-card class="upload-card">
          <el-upload
            drag
            :auto-upload="false"
            :on-change="handleFileChange"
            :limit="1"
            accept=".pdf,.doc,.docx,.txt"
          >
            <el-icon :size="60"><UploadFilled /></el-icon>
            <div class="el-upload__text">
              将文档拖到此处，或<em>点击上传</em>
            </div>
            <template #tip>
              <div class="el-upload__tip">
                支持 PDF、Word、文本文档，最大100MB
              </div>
            </template>
          </el-upload>
          <el-button
            v-if="selectedFile"
            type="primary"
            @click="handleBuildIndex"
            :loading="buildingIndex"
            style="margin-top: 16px"
          >
            建立搜索索引
          </el-button>
        </el-card>

        <el-card v-if="documentId" class="search-card">
          <h3>搜索文档</h3>
          <el-input
            v-model="searchQuery"
            placeholder="输入要搜索的关键词"
            @keyup.enter="handleSearch"
            :loading="searching"
          >
            <template #append>
              <el-button :icon="Search" @click="handleSearch" />
            </template>
          </el-input>

          <el-form :model="searchOptions" label-width="100px" style="margin-top: 16px">
            <el-form-item label="区分大小写">
              <el-switch v-model="searchOptions.case_sensitive" />
            </el-form-item>
            <el-form-item label="全词匹配">
              <el-switch v-model="searchOptions.whole_word" />
            </el-form-item>
            <el-form-item label="正则表达式">
              <el-switch v-model="searchOptions.regex" />
            </el-form-item>
          </el-form>

          <div class="results-section" v-if="searchResults.length > 0">
            <h4>搜索结果 ({{ searchResults.length }} 条)</h4>
            <el-collapse v-model="activeResults">
              <el-collapse-item
                v-for="(result, index) in searchResults"
                :key="index"
                :name="index"
              >
                <template #title>
                  <span class="result-title">第 {{ result.page_index + 1 }} 页</span>
                </template>
                <div class="result-content">
                  <div v-if="result.highlights && result.highlights.length > 0" class="highlights">
                    <div v-for="(highlight, i) in result.highlights" :key="i" class="highlight">
                      {{ highlight }}
                    </div>
                  </div>
                  <div class="text-preview">{{ result.text }}</div>
                </div>
              </el-collapse-item>
            </el-collapse>
          </div>

          <el-empty v-else-if="searched && searchResults.length === 0" description="未找到匹配结果" />
        </el-card>
      </el-main>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { UploadFilled, ArrowLeft, Search } from '@element-plus/icons-vue'
import type { UploadFile } from 'element-plus'
import { api } from '@/services/api'

const router = useRouter()
const selectedFile = ref<File | null>(null)
const buildingIndex = ref(false)
const searching = ref(false)
const documentId = ref('')
const searchQuery = ref('')
const searchResults = ref<any[]>([])
const searched = ref(false)
const activeResults = ref<number[]>([])

const searchOptions = ref({
  case_sensitive: false,
  whole_word: false,
  regex: false,
})

function handleFileChange(file: UploadFile) {
  if (file.raw) {
    selectedFile.value = file.raw
  }
}

async function handleBuildIndex() {
  if (!selectedFile.value) return

  buildingIndex.value = true

  try {
    const formData = new FormData()
    formData.append('file', selectedFile.value)

    const result = await fetch('/api/v1/search/index/' + Date.now(), {
      method: 'POST',
      body: formData,
    }).then(res => res.json())

    if (result.success) {
      documentId.value = result.document_id
      ElMessage.success(`索引建立成功，共 ${result.total_pages} 页`)
    } else {
      ElMessage.error(`索引建立失败：${result.error}`)
    }
  } catch (error: any) {
    ElMessage.error(`索引建立失败：${error.message}`)
  } finally {
    buildingIndex.value = false
  }
}

async function handleSearch() {
  if (!searchQuery.value || !documentId.value) return

  searching.value = true
  searched.value = true

  try {
    const params = new URLSearchParams({
      query: searchQuery.value,
      ...searchOptions.value,
    })

    const results = await fetch(`/api/v1/search/${documentId.value}?${params.toString()}`)
      .then(res => res.json())

    searchResults.value = results
  } catch (error: any) {
    ElMessage.error(`搜索失败：${error.message}`)
  } finally {
    searching.value = false
  }
}
</script>

<style scoped>
.search-view {
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

.search-card {
  margin-top: 24px;
}

.results-section {
  margin-top: 24px;
}

.result-title {
  font-weight: 600;
}

.result-content {
  padding: 12px;
}

.highlights {
  background-color: #fff7e6;
  border: 1px solid #ffd591;
  border-radius: 4px;
  padding: 12px;
  margin-bottom: 12px;
}

.highlight {
  padding: 4px 0;
  border-bottom: 1px dashed #d9d9d9;
}

.highlight:last-child {
  border-bottom: none;
}

.text-preview {
  color: #666;
  font-size: 14px;
  max-height: 150px;
  overflow-y: auto;
}
</style>
