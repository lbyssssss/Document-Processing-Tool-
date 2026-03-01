<template>
  <div class="page-view">
    <el-container>
      <el-header>
        <el-button @click="$router.back()">
          <el-icon><ArrowLeft /></el-icon>
          返回
        </el-button>
        <h2>页面管理</h2>
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
            @change="loadDocumentPages"
          >
            <el-option
              v-for="doc in documents"
              :key="doc.id"
              :label="doc.name"
              :value="doc.id"
            />
          </el-select>
        </el-card>

        <!-- 页面列表 -->
        <el-card v-if="selectedDocumentId" class="pages-card">
          <template #header>
            <div class="pages-header">
              <span>页面列表</span>
              <div class="header-actions">
                <el-button size="small" @click="handleInsertBlankPage">
                  <el-icon><Plus /></el-icon>
                  插入空白页
                </el-button>
              </div>
            </div>
          </template>

          <div class="pages-grid">
            <div
              v-for="(page, index) in pages"
              :key="index"
              class="page-item"
              :class="{ selected: selectedPageIndex === index }"
              @click="selectPage(index)"
            >
              <div class="page-number">第 {{ index + 1 }} 页</div>
              <div class="page-size">{{ page.width }} x {{ page.height }}</div>
              <div class="page-rotation" v-if="page.rotation !== 0">
                旋转: {{ page.rotation }}°
              </div>
            </div>

            <el-empty v-if="pages.length === 0" description="暂无页面" />
          </div>
        </el-card>

        <!-- 页面操作 -->
        <el-card v-if="selectedPageIndex !== -1" class="operations-card">
          <h3>页面操作 - 第 {{ selectedPageIndex + 1 }} 页</h3>

          <div class="operation-buttons">
            <el-button-group>
              <el-button @click="handleRotate(90)">
                <el-icon><RefreshRight /></el-icon>
                旋转 90°
              </el-button>
              <el-button @click="handleRotate(180)">
                <el-icon><RefreshRight /></el-icon>
                旋转 180°
              </el-button>
              <el-button @click="handleRotate(270)">
                <el-icon><RefreshRight /></el-icon>
                旋转 270°
              </el-button>
            </el-button-group>

            <el-button-group>
              <el-button @click="handleMoveUp" :disabled="selectedPageIndex === 0">
                <el-icon><ArrowUp /></el-icon>
                上移
              </el-button>
              <el-button @click="handleMoveDown" :disabled="selectedPageIndex === pages.length - 1">
                <el-icon><ArrowDown /></el-icon>
                下移
              </el-button>
            </el-button-group>

            <el-button-group>
              <el-button type="primary" @click="handleSplit">
                <el-icon><Scissors /></el-icon>
                拆分页面
              </el-button>
              <el-button type="danger" @click="handleDelete">
                <el-icon><Delete /></el-icon>
                删除页面
              </el-button>
            </el-button-group>
          </div>

          <!-- 合并操作 -->
          <div class="merge-section">
            <h4>合并页面</h4>
            <el-checkbox-group v-model="mergeSelection" @change="handleMergeSelectionChange">
              <el-checkbox
                v-for="(page, index) in pages"
                :key="index"
                :label="index"
                :disabled="index === selectedPageIndex"
              >
                第 {{ index + 1 }} 页
              </el-checkbox>
            </el-checkbox-group>
            <el-button
              type="primary"
              :disabled="mergeSelection.length < 2"
              @click="handleMerge"
            >
              合并选中的页面
            </el-button>
          </div>
        </el-card>
      </el-main>
    </el-container>

    <!-- 插入空白页对话框 -->
    <el-dialog v-model="insertDialogVisible" title="插入空白页" width="400px">
      <el-form :model="insertForm" label-width="100px">
        <el-form-item label="插入位置">
          <el-input-number
            v-model="insertForm.index"
            :min="0"
            :max="pages.length"
            controls-position="right"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="insertDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmInsert">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  ArrowLeft,
  Plus,
  RefreshRight,
  ArrowUp,
  ArrowDown,
  Delete,
  Scissors,
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { api } from '@/services/api'

const router = useRouter()

// 文档列表（模拟数据）
const documents = ref([
  { id: 'doc1', name: '文档1.pdf' },
  { id: 'doc2', name: '文档2.pdf' },
  { id: 'doc3', name: '文档3.pdf' },
])

const selectedDocumentId = ref('')
const pages = ref<any[]>([])
const selectedPageIndex = ref(-1)
const insertDialogVisible = ref(false)
const mergeSelection = ref<number[]>([])

// 插入表单
const insertForm = ref({
  index: 0,
})

async function loadDocumentPages() {
  if (!selectedDocumentId.value) return

  try {
    const result = await api.getDocumentPagesInfo(selectedDocumentId.value)
    pages.value = result.pages
    selectedPageIndex.value = -1
    mergeSelection.value = []
  } catch (error: any) {
    ElMessage.error(`加载页面信息失败: ${error.message}`)
  }
}

function selectPage(index: number) {
  selectedPageIndex.value = index
}

async function handleRotate(degrees: number) {
  if (selectedPageIndex.value === -1) return

  try {
    const result = await api.rotatePage(
      selectedDocumentId.value,
      selectedPageIndex.value + 1,
      { degrees }
    )
    if (result.success) {
      pages.value[selectedPageIndex.value].rotation =
        (pages.value[selectedPageIndex.value].rotation + degrees) % 360
      ElMessage.success('页面旋转成功')
    }
  } catch (error: any) {
    ElMessage.error(`旋转页面失败: ${error.message}`)
  }
}

async function handleMoveUp() {
  if (selectedPageIndex.value <= 0) return

  try {
    const result = await api.movePage(selectedDocumentId.value, {
      from_index: selectedPageIndex.value,
      to_index: selectedPageIndex.value - 1,
    })
    if (result.success) {
      const temp = pages.value[selectedPageIndex.value]
      pages.value[selectedPageIndex.value] = pages.value[selectedPageIndex.value - 1]
      pages.value[selectedPageIndex.value - 1] = temp
      selectedPageIndex.value -= 1
      ElMessage.success('页面上移成功')
    }
  } catch (error: any) {
    ElMessage.error(`移动页面失败: ${error.message}`)
  }
}

async function handleMoveDown() {
  if (selectedPageIndex.value >= pages.value.length - 1) return

  try {
    const result = await api.movePage(selectedDocumentId.value, {
      from_index: selectedPageIndex.value,
      to_index: selectedPageIndex.value + 1,
    })
    if (result.success) {
      const temp = pages.value[selectedPageIndex.value]
      pages.value[selectedPageIndex.value] = pages.value[selectedPageIndex.value + 1]
      pages.value[selectedPageIndex.value + 1] = temp
      selectedPageIndex.value += 1
      ElMessage.success('页面下移成功')
    }
  } catch (error: any) {
    ElMessage.error(`移动页面失败: ${error.message}`)
  }
}

async function handleDelete() {
  if (selectedPageIndex.value === -1) return

  try {
    await ElMessageBox.confirm('确定要删除此页面吗？', '确认删除', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })

    const result = await api.deletePage(
      selectedDocumentId.value,
      selectedPageIndex.value + 1
    )
    if (result.success) {
      pages.value.splice(selectedPageIndex.value, 1)
      selectedPageIndex.value = -1
      ElMessage.success('页面删除成功')
    }
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(`删除页面失败: ${error.message}`)
    }
  }
}

async function handleSplit() {
  if (selectedPageIndex.value === -1) return

  try {
    const result = await api.splitPage(
      selectedDocumentId.value,
      selectedPageIndex.value + 1
    )
    if (result.success) {
      await loadDocumentPages()
      ElMessage.success(result.note || '页面拆分成功')
    }
  } catch (error: any) {
    ElMessage.error(`拆分页面失败: ${error.message}`)
  }
}

function handleInsertBlankPage() {
  insertForm.value.index = selectedPageIndex.value !== -1 ? selectedPageIndex.value + 1 : pages.value.length
  insertDialogVisible.value = true
}

async function confirmInsert() {
  try {
    const result = await api.insertPage(selectedDocumentId.value, {
      index: insertForm.value.index,
    })
    if (result.success) {
      await loadDocumentPages()
      insertDialogVisible.value = false
      ElMessage.success('空白页插入成功')
    }
  } catch (error: any) {
    ElMessage.error(`插入页面失败: ${error.message}`)
  }
}

function handleMergeSelectionChange() {
  // 自动包含当前选中的页面
  if (!mergeSelection.value.includes(selectedPageIndex.value) && selectedPageIndex.value !== -1) {
    mergeSelection.value.push(selectedPageIndex.value)
  }
}

async function handleMerge() {
  if (mergeSelection.value.length < 2) {
    ElMessage.warning('请至少选择2个页面进行合并')
    return
  }

  try {
    const result = await api.mergePages(selectedDocumentId.value, {
      indices: mergeSelection.value.map(i => i + 1),  // 转换为1-based
    })
    if (result.success) {
      ElMessage.success(`成功合并 ${result.merged_pages} 个页面`)
    }
  } catch (error: any) {
    ElMessage.error(`合并页面失败: ${error.message}`)
  }
}
</script>

<style scoped>
.page-view {
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
.pages-card,
.operations-card {
  margin-bottom: 24px;
}

.pages-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.pages-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 16px;
  padding: 16px 0;
}

.page-item {
  border: 2px solid #eee;
  border-radius: 8px;
  padding: 16px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s;
}

.page-item:hover {
  border-color: #409eff;
}

.page-item.selected {
  border-color: #409eff;
  background-color: #ecf5ff;
}

.page-number {
  font-weight: 500;
  color: #409eff;
  margin-bottom: 8px;
}

.page-size {
  font-size: 12px;
  color: #999;
  margin-bottom: 4px;
}

.page-rotation {
  font-size: 12px;
  color: #f56c6c;
}

.operations-card h3 {
  margin-bottom: 16px;
}

.operation-buttons {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-bottom: 24px;
}

.merge-section {
  border-top: 1px solid #eee;
  padding-top: 16px;
}

.merge-section h4 {
  margin-bottom: 12px;
}

.merge-section .el-checkbox-group {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 12px;
  margin-bottom: 16px;
}

.merge-section .el-button {
  width: 100%;
}
</style>
