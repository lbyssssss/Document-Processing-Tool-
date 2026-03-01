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
        <!-- 文档选择 -->
        <el-card class="document-card">
          <template #header>
            <span>选择文档</span>
          </template>
          <el-select
            v-model="selectedDocumentId"
            placeholder="请选择文档"
            @change="handleDocumentChange"
          >
            <el-option
              v-for="doc in documents"
              :key="doc.id"
              :label="doc.name"
              :value="doc.id"
            />
          </el-select>
        </el-card>

        <!-- 搜索框 -->
        <el-card v-if="selectedDocumentId" class="search-card">
          <el-input
            v-model="searchQuery"
            placeholder="输入关键词搜索..."
            clearable
            @keyup.enter="handleSearch"
          >
            <template #append>
              <el-button :icon="Search" @click="handleSearch" />
            </template>
          </el-input>

          <!-- 搜索选项 -->
          <div class="search-options">
            <el-checkbox v-model="options.case_sensitive">区分大小写</el-checkbox>
            <el-checkbox v-model="options.whole_word">全词匹配</el-checkbox>
            <el-checkbox v-model="options.regex">正则表达式</el-checkbox>
          </div>
        </el-card>

        <!-- 搜索结果 -->
        <el-card v-if="selectedDocumentId" class="results-card">
          <template #header>
            <div class="results-header">
              <span>搜索结果</span>
              <el-tag v-if="results.length > 0" type="info">
                找到 {{ results.length }} 条
              </el-tag>
              <el-tag v-else type="warning">未找到匹配</el-tag>
            </div>
          </template>

          <div class="results-list">
            <div
              v-for="(result, index) in results"
              :key="index"
              class="result-item"
              :class="{ active: currentResultIndex === index }"
            >
              <div class="result-header">
                <span class="result-page">第 {{ result.page_index + 1 }} 页</span>
                <el-tag size="small" type="info">匹配</el-tag>
              </div>

              <div class="result-content">
                {{ result.text }}
              </div>

              <!-- 高亮片段 -->
              <div v-if="result.highlights && result.highlights.length > 0" class="result-highlights">
                <div
                  v-for="(highlight, hIndex) in result.highlights"
                  :key="hIndex"
                  class="highlight-item"
                >
                  ...{{ highlight }}...
                </div>
              </div>
            </div>

            <el-empty
              v-if="results.length === 0 && hasSearched"
              description="未找到匹配结果"
              :image-size="100"
            />
            <el-empty
              v-if="!hasSearched"
              description="输入关键词开始搜索"
              :image-size="100"
            />
          </div>

          <!-- 导航按钮 -->
          <div v-if="results.length > 0" class="result-navigation">
            <el-button
              :disabled="currentResultIndex <= 0"
              @click="navigateResult(-1)"
            >
              <el-icon><ArrowUp /></el-icon>
              上一条
            </el-button>
            <span class="nav-counter">
              {{ currentResultIndex + 1 }} / {{ results.length }}
            </span>
            <el-button
              :disabled="currentResultIndex >= results.length - 1"
              @click="navigateResult(1)"
            >
              下一条
              <el-icon><ArrowDown /></el-icon>
            </el-button>
          </div>
        </el-card>

        <!-- 索引信息 -->
        <el-card v-if="indexInfo" class="index-info-card">
          <template #header>
            <span>索引信息</span>
          </template>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="文档ID">
              {{ selectedDocumentId }}
            </el-descriptions-item>
            <el-descriptions-item label="已索引页面">
              {{ indexInfo.indexed_pages }} / {{ indexInfo.total_pages }}
            </el-descriptions-item>
            <el-descriptions-item label="索引状态">
              <el-tag :type="indexInfo.indexed ? 'success' : 'warning'">
                {{ indexInfo.indexed ? '已索引' : '未索引' }}
              </el-tag>
            </el-descriptions-item>
          </el-descriptions>
          <div class="index-actions">
            <el-button type="primary" @click="buildIndex" :loading="indexing">
              {{ indexInfo.indexed ? '重建索引' : '创建索引' }}
            </el-button>
          </div>
        </el-card>
      </el-main>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ArrowLeft, Search, ArrowUp, ArrowDown } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { api } from '@/services/api'

const router = useRouter()

// 文档列表（模拟数据）
const documents = ref([
  { id: 'doc1', name: '文档1.pdf', totalPages: 10 },
  { id: 'doc2', name: '文档2.pdf', totalPages: 15 },
  { id: 'doc3', name: '文档3.pdf', totalPages: 8 },
])

const selectedDocumentId = ref('')
const searchQuery = ref('')
const results = ref<any[]>([])
const currentResultIndex = ref(0)
const hasSearched = ref(false)
const indexing = ref(false)
const indexInfo = ref<any>(null)

// 搜索选项
const options = ref({
  case_sensitive: false,
  whole_word: false,
  regex: false,
})

async function handleDocumentChange() {
  // 加载索引信息
  await loadIndexInfo()
  // 清空搜索结果
  results.value = []
  hasSearched.value = false
  currentResultIndex.value = 0
}

async function loadIndexInfo() {
  if (!selectedDocumentId.value) return

  try {
    const info = await api.getIndexInfo(selectedDocumentId.value)
    indexInfo.value = info
  } catch (error: any) {
    console.error('加载索引信息失败:', error)
  }
}

async function buildIndex() {
  if (!selectedDocumentId.value) {
    ElMessage.warning('请先选择文档')
    return
  }

  indexing.value = true
  try {
    // 这里需要上传文件来建立索引
    // 暂时使用模拟数据
    await new Promise(resolve => setTimeout(resolve, 1000))

    indexInfo.value = {
      indexed: true,
      page_count: 10,
    }

    ElMessage.success('索引创建成功')
  } catch (error: any) {
    ElMessage.error(`创建索引失败: ${error.message}`)
  } finally {
    indexing.value = false
  }
}

async function handleSearch() {
  if (!searchQuery.value.trim()) {
    ElMessage.warning('请输入搜索关键词')
    return
  }

  if (!selectedDocumentId.value) {
    ElMessage.warning('请先选择文档')
    return
  }

  if (!indexInfo.value?.indexed) {
    ElMessage.warning('文档尚未索引，请先创建索引')
    return
  }

  try {
    const data = await api.search(selectedDocumentId.value, searchQuery.value, options.value)
    results.value = data
    hasSearched.value = true
    currentResultIndex.value = 0
  } catch (error: any) {
    ElMessage.error(`搜索失败: ${error.message}`)
  }
}

function navigateResult(delta: number) {
  const newIndex = currentResultIndex.value + delta
  if (newIndex >= 0 && newIndex < results.value.length) {
    currentResultIndex.value = newIndex
    // 滚动到结果位置
    scrollToResult(newIndex)
  }
}

function scrollToResult(index: number) {
  const items = document.querySelectorAll('.result-item')
  if (items[index]) {
    items[index].scrollIntoView({ behavior: 'smooth', block: 'nearest' })
  }
}

onMounted(() => {
  // 如果有文档ID，自动加载
  if (selectedDocumentId.value) {
    handleDocumentChange()
  }
})
</script>

<style scoped>
.search-view {
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
.search-card,
.results-card,
.index-info-card {
  margin-bottom: 24px;
}

.search-options {
  margin-top: 16px;
  display: flex;
  gap: 24px;
}

.results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.results-list {
  max-height: 600px;
  overflow-y: auto;
}

.result-item {
  padding: 16px;
  border: 1px solid #eee;
  border-radius: 8px;
  margin-bottom: 12px;
  transition: all 0.2s;
}

.result-item:hover {
  border-color: #409eff;
}

.result-item.active {
  background-color: #ecf5ff;
  border-color: #409eff;
}

.result-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.result-page {
  font-weight: 500;
  color: #409eff;
}

.result-content {
  color: #333;
  line-height: 1.6;
  margin-bottom: 8px;
}

.result-highlights {
  margin-top: 8px;
  padding: 8px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.highlight-item {
  color: #666;
  font-size: 13px;
  margin-bottom: 4px;
}

.result-navigation {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #eee;
}

.nav-counter {
  color: #666;
  font-size: 14px;
}

.index-actions {
  margin-top: 16px;
}
</style>
