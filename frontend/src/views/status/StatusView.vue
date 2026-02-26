<template>
  <div class="status-view">
    <el-container>
      <el-card class="status-card">
        <h2>部署状态说明</h2>
        
        <el-alert title="预览环境限制" type="warning" :closable="false" show-icon>
          在预览环境中，API 功能无法使用。前端只提供静态文件，
          无法访问本地后端（http://localhost:8000）。
        </el-alert>
        
        <el-alert title="如何测试完整功能" type="info" :closable="false" show-icon>
          在本地环境中运行以下命令来测试完整功能：
          <el-divider />
          <p><strong>后端：</strong></p>
          <code>cd /workspace/backend && python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000</code>
          
          <p><strong>前端（开发模式）：</strong></p>
          <code>cd /workspace/frontend && npm run dev</code>
          
          <p>前端会通过代理访问后端 API，支持完整功能。</p>
        </el-alert>
        
        <el-divider />
        
        <h3>当前状态</h3>
        <el-descriptions :column="1" border>
          <el-descriptions-item label="预览环境">
            <el-icon><Connection /></el-icon>
            只提供静态文件，API 请求会失败
          </el-descriptions-item>
          <el-descriptions-item label="后端状态">
            <el-icon><Loading /></el-icon>
            正常运行（http://localhost:8000）
          </el-descriptions-item>
          <el-descriptions-item label="GitHub 仓库">
            <el-icon><Link /></el-icon>
            <a href="https://github.com/lbyssssss/Document-Processing-Tool-" target="_blank">查看仓库</a>
          </el-descriptions-item>
        </el-descriptions>
      </el-card>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const deployStatus = {
  preview: {
    apiAvailable: false,
    description: '预览环境只提供静态文件，无法访问本地后端',
    icon: 'Connection',
  },
  local: {
    apiAvailable: true,
    description: '本地开发模式，支持完整功能',
    icon: 'Loading',
  },
}
</script>

<style scoped>
.status-view {
  padding: 24px;
}

.status-card {
  max-width: 800px;
  margin: 0 auto;
}
</style>
