<template>
  <div class="home-view">
    <el-container>
      <el-header>
        <h1>文档处理工具</h1>
        <nav class="nav-menu">
          <el-button @click="$router.push('/conversion')">格式转换</el-button>
          <el-button @click="$router.push('/search')">全文检索</el-button>
          <el-button @click="$router.push('/annotation')">批注编辑</el-button>
          <el-button @click="$router.push('/page-management')">页面管理</el-button>
          <el-button @click="$router.push('/merge')">文档拼接</el-button>
        </nav>
      </el-header>
      <el-main>
        <el-card class="welcome-card">
          <h2>欢迎使用文档处理工具</h2>
          <p>支持PDF、Word、Excel、PPT、图片等常见格式的文档转换、检索、批注和页面管理。</p>
          <div class="feature-grid">
            <el-card class="feature-item" shadow="hover" @click="$router.push('/conversion')">
              <el-icon :size="40"><Document /></el-icon>
              <h3>格式转换</h3>
              <p>支持多种文档格式之间的相互转换</p>
            </el-card>
            <el-card class="feature-item" shadow="hover" @click="$router.push('/search')">
              <el-icon :size="40"><Search /></el-icon>
              <h3>全文检索</h3>
              <p>快速定位文档中的关键词</p>
            </el-card>
            <el-card class="feature-item" shadow="hover" @click="$router.push('/annotation')">
              <el-icon :size="40"><Edit /></el-icon>
              <h3>批注编辑</h3>
              <p>在文档上添加批注和标记</p>
            </el-card>
            <el-card class="feature-item" shadow="hover" @click="$router.push('/page-management')">
              <el-icon :size="40"><Memo /></el-icon>
              <h3>页面管理</h3>
              <p>对文档页面进行插入、删除、旋转等操作</p>
            </el-card>
            <el-card class="feature-item" shadow="hover" @click="$router.push('/merge')">
              <el-icon :size="40"><Link /></el-icon>
              <h3>文档拼接</h3>
              <p>将多个文档的指定页面合并为一个新文档</p>
            </el-card>
            <el-card class="feature-item" shadow="hover" @click="$router.push('/status')">
              <el-icon :size="40"><InfoFilled /></el-icon>
              <h3>部署状态</h3>
              <p>查看当前部署环境和说明</p>
            </el-card>
          </div>
        </el-card>
      </el-main>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { Document, Search, Edit, Memo, Link, InfoFilled } from '@element-plus/icons-vue'
</script>

<style scoped>
.home-view {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.el-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
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

.welcome-card {
  text-align: center;
  max-width: 800px;
  margin: 0 auto;
}

.welcome-card h2 {
  margin-bottom: 16px;
  font-size: 28px;
}

.welcome-card p {
  color: #666;
  margin-bottom: 32px;
  font-size: 16px;
}

.feature-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-top: 32px;
}

.feature-item {
  padding: 24px;
  text-align: center;
  cursor: pointer;
  transition: transform 0.2s;
}

.feature-item:hover {
  transform: translateY(-4px);
}

.feature-item .el-icon {
  color: #409eff;
  margin-bottom: 16px;
}

.feature-item h3 {
  margin-bottom: 8px;
  font-size: 18px;
}

.feature-item p {
  color: #666;
  font-size: 14px;
}
</style>
