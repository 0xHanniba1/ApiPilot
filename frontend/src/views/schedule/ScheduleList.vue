<template>
  <div class="page-container">
    <div class="page-header">
      <h2 class="page-title">定时任务</h2>
      <el-button type="primary">
        <el-icon><Plus /></el-icon>
        新建任务
      </el-button>
    </div>
    <el-alert type="info" :closable="false">
      定时任务管理页面正在开发中...
    </el-alert>
  </div>
</template>

<script setup>
import { Plus } from '@element-plus/icons-vue'
</script>
