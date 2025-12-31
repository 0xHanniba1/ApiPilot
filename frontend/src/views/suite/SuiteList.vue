<template>
  <div class="page-container">
    <div class="page-header">
      <h2 class="page-title">测试集</h2>
      <el-button type="primary">
        <el-icon><Plus /></el-icon>
        新建测试集
      </el-button>
    </div>
    <el-alert type="info" :closable="false">
      测试集管理页面正在开发中...
    </el-alert>
  </div>
</template>

<script setup>
import { Plus } from '@element-plus/icons-vue'
</script>
