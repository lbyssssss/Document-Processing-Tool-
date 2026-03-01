<template>
  <div class="page-manager">
    <div class="manager-header">
      <h3>页面管理</h3>
      <div class="header-actions">
        <el-button size="small" @click="refreshPages">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>
    </div>

    <div class="manager-content">
      <el-tabs v-model="activeTab">
        <el-tab-pane label="页面列表" name="list">
          <div class="page-list">
            <el-empty v-if="pages.length === 0" description="暂无页面" />
            
            <div v-else class="page-grid">
              <div
                v-for="page in pages"
                :key="page.page_number"
                class="page-card"
              >
                <div class="page-thumbnail">
                  <img
                    v-if="page.thumbnail"
                    :src="`data:image/png;base64,${page.thumbnail}`"
                    :alt="`第${page.page_number}页`"
                  />
                  <div v-else class="placeholder">
                    第{{ page.page_number }}页
                  </div>
                </div>
                <div class="page-info">
                  <span class="page-number">第{{ page.page_number }}页</span>
                  <span class="page-size">
                    {{ page.width }} x {{ page.height }}
                  </span>
                </div>
                <div class="page-actions">
                  <el-button-group>
                    <el-tooltip content="旋转90度">
                      <el-button size="small" @click="rotatePage(page.page_number, 90)">
                        <el-icon><RefreshRight /></el-icon>
                      </el-button>
                    </el-tooltip>
                    <el-tooltip content="旋转180度">
                      <el-button size="small" @click="rotatePage(page.page_number, 180)">
                        <el-icon><RefreshRight /><RefreshRight /></el-icon>
                      </el-button>
                    </el-tooltip>
                    <el-tooltip content="旋转270度">
                      <el-button size="small" @click="rotatePage(page.page_number, 270)">
                        <el-icon><RefreshRight /><RefreshRight /><RefreshRight /></el-icon>
                      </el-button>
                    </el-tooltip>
                    <el-tooltip content="移动">
                      <el-button size="small" @click="showMoveDialog(page)">
                        <el-icon><Rank /></el-icon>
                      </el-button>
                    </el-tooltip>
                    <el-tooltip content="拆分">
                      <el-button size="small" @click="showSplitDialog(page)">
                        <el-icon><Scissors /></el-icon>
                      </el-button>
                    </el-tooltip>
                    <el-tooltip content="删除">
                      <el-button size="small" type="danger" @click="deletePage(page.page_number)">
                        <el-icon><Delete /></el-icon>
                      </el-button>
                    </el-tooltip>
                  </el-button-group>
                </div>
              </div>
            </div>
          </div>
        </el-tab-pane>

        <el-tab-pane label="批量操作" name="batch">
          <div class="batch-operations">
            <el-card>
              <h4>批量操作</h4>
              <el-form :model="batchForm" label-width="120px">
                <el-form-item label="插入空白页">
                  <el-input-number v-model="batchForm.insertPosition" :min="1" :max="pages.length + 1" />
                  <el-button type="primary" style="margin-left: 8px" @click="insertBlankPage">
                    插入
                  </el-button>
                </el-form-item>
                <el-form-item label="合并页面">
                  <el-select
                    v-model="batchForm.mergePages"
                    multiple
                    placeholder="选择要合并的页面"
                  >
                    <el-option
                      v-for="page in pages"
                      :key="page.page_number"
                      :label="`第${page.page_number}页`"
                      :value="page.page_number"
                    />
                  </el-select>
                  <el-button type="primary" style="margin-left: 8px" @click="mergeSelectedPages">
                    合并
                  </el-button>
                </el-form-item>
              </el-form>
            </el-card>
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>

    <!-- 移动页面对话框 -->
    <el-dialog
      v-model="showMoveDialogVisible"
      title="移动页面"
      width="400px"
    >
      <el-form :model="moveForm" label-width="100px">
        <el-form-item label="当前页码">
          <span>{{ moveForm.currentPage }}</span>
        </el-form-item>
        <el-form-item label="新位置">
          <el-input-number
            v-model="moveForm.newPageNumber"
            :min="1"
            :max="pages.length"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showMoveDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="movePage">确定</el-button>
      </template>
    </el-dialog>

    <!-- 拆分页面对话框 -->
    <el-dialog
      v-model="showSplitDialogVisible"
      title="拆分页面"
      width="400px"
    >
      <el-form :model="splitForm" label-width="100px">
        <el-form-item label="当前页码">
          <span>{{ splitForm.currentPage }}</span>
        </el-form-item>
        <el-form-item label="拆分方式">
          <el-radio-group v-model="splitForm.splitType">
            <el-radio value="vertical">垂直拆分</el-radio>
            <el-radio value="horizontal">水平拆分</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showSplitDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="splitPage">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { Refresh, RefreshRight, Rank, Scissors, Delete } from '@element-plus/icons-vue'
import { api } from '@/services/api'
import { ElMessage, ElMessageBox } from 'element-plus'

interface Page {
  page_number: number
  width: number
  height: number
  rotation: number
  thumbnail?: string
}

interface Props {
  documentId: string
}

const props = defineProps<Props>()

const pages = ref<Page[]>([])
const activeTab = ref('list')
const showMoveDialogVisible = ref(false)
const showSplitDialogVisible = ref(false)

const moveForm = ref({
  currentPage: 0,
  newPageNumber: 1,
})

const splitForm = ref({
  currentPage: 0,
  splitType: 'vertical' as 'vertical' | 'horizontal',
})

const batchForm = ref({
  insertPosition: 1,
  mergePages: [] as number[],
})

async function loadPages() {
  try {
    const result = await api.getPages(props.documentId)
    if (result.success) {
      pages.value = result.pages
    }
  } catch (error: any) {
    ElMessage.error(`加载页面失败: ${error.message}`)
  }
}

async function refreshPages() {
  await loadPages()
  ElMessage.success('页面已刷新')
}

async function rotatePage(pageNumber: number, degrees: number) {
  try {
    const result = await api.rotatePage(props.documentId, pageNumber, degrees)
    if (result.success) {
      ElMessage.success(`页面旋转${degrees}度成功`)
      await loadPages()
    } else {
      ElMessage.error(result.message || '旋转失败')
    }
  } catch (error: any) {
    ElMessage.error(`旋转失败: ${error.message}`)
  }
}

function showMoveDialog(page: Page) {
  moveForm.value.currentPage = page.page_number
  moveForm.value.newPageNumber = page.page_number
  showMoveDialogVisible.value = true
}

async function movePage() {
  try {
    const result = await api.movePage(
      props.documentId,
      moveForm.value.currentPage,
      moveForm.value.newPageNumber
    )
    if (result.success) {
      ElMessage.success('页面移动成功')
      showMoveDialogVisible.value = false
      await loadPages()
    } else {
      ElMessage.error(result.message || '移动失败')
    }
  } catch (error: any) {
    ElMessage.error(`移动失败: ${error.message}`)
  }
}

async function deletePage(pageNumber: number) {
  try {
    await ElMessageBox.confirm(
      `确定要删除第${pageNumber}页吗？`,
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )

    const result = await api.deletePage(props.documentId, pageNumber)
    if (result.success) {
      ElMessage.success('页面删除成功')
      await loadPages()
    } else {
      ElMessage.error(result.message || '删除失败')
    }
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(`删除失败: ${error.message}`)
    }
  }
}

function showSplitDialog(page: Page) {
  splitForm.value.currentPage = page.page_number
  splitForm.value.splitType = 'vertical'
  showSplitDialogVisible.value = true
}

async function splitPage() {
  try {
    const result = await api.splitPage(
      props.documentId,
      splitForm.value.currentPage,
      splitForm.value.splitType
    )
    if (result.success) {
      ElMessage.success('页面拆分成功')
      showSplitDialogVisible.value = false
      await loadPages()
    } else {
      ElMessage.error(result.message || '拆分失败')
    }
  } catch (error: any) {
    ElMessage.error(`拆分失败: ${error.message}`)
  }
}

async function insertBlankPage() {
  try {
    const result = await api.insertPage(props.documentId, batchForm.value.insertPosition)
    if (result.success) {
      ElMessage.success('空白页插入成功')
      await loadPages()
    } else {
      ElMessage.error(result.message || '插入失败')
    }
  } catch (error: any) {
    ElMessage.error(`插入失败: ${error.message}`)
  }
}

async function mergeSelectedPages() {
  if (batchForm.value.mergePages.length < 2) {
    ElMessage.warning('请至少选择2个页面进行合并')
    return
  }

  try {
    const result = await api.mergePages(props.documentId, batchForm.value.mergePages)
    if (result.success) {
      ElMessage.success('页面合并成功')
      batchForm.value.mergePages = []
      await loadPages()
    } else {
      ElMessage.error(result.message || '合并失败')
    }
  } catch (error: any) {
    ElMessage.error(`合并失败: ${error.message}`)
  }
}

onMounted(() => {
  loadPages()
})

watch(() => props.documentId, () => {
  if (props.documentId) {
    loadPages()
  }
})
</script>

<style scoped>
.page-manager {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.manager-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid #eee;
}

.manager-header h3 {
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.manager-content {
  flex: 1;
  overflow: hidden;
  padding: 16px;
}

.page-list {
  height: 100%;
  overflow-y: auto;
}

.page-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
}

.page-card {
  border: 1px solid #eee;
  border-radius: 8px;
  overflow: hidden;
  transition: all 0.2s;
}

.page-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.page-thumbnail {
  aspect-ratio: 0.707;
  background: #f5f5f5;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.page-thumbnail img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.placeholder {
  color: #909399;
  font-size: 14px;
}

.page-info {
  padding: 8px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-top: 1px solid #eee;
}

.page-number {
  font-weight: bold;
  color: #303133;
}

.page-size {
  font-size: 12px;
  color: #909399;
}

.page-actions {
  padding: 8px;
  border-top: 1px solid #eee;
}

.batch-operations {
  max-width: 600px;
  margin: 0 auto;
}

.batch-operations h4 {
  margin-bottom: 16px;
}
</style>
