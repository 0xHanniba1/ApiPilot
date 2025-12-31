<template>
  <header class="app-header">
    <div class="header-left">
      <el-icon class="collapse-btn" @click="toggleSidebar">
        <Fold v-if="!collapsed" />
        <Expand v-else />
      </el-icon>
      <el-breadcrumb separator="/">
        <el-breadcrumb-item v-for="item in breadcrumbs" :key="item.path">
          <router-link v-if="item.path" :to="item.path">{{ item.title }}</router-link>
          <span v-else>{{ item.title }}</span>
        </el-breadcrumb-item>
      </el-breadcrumb>
    </div>
    <div class="header-right">
      <el-tooltip content="刷新" placement="bottom">
        <el-icon class="header-icon" @click="handleRefresh">
          <Refresh />
        </el-icon>
      </el-tooltip>
      <el-tooltip content="全屏" placement="bottom">
        <el-icon class="header-icon" @click="toggleFullscreen">
          <FullScreen />
        </el-icon>
      </el-tooltip>
      <el-dropdown trigger="click">
        <div class="user-info">
          <el-avatar :size="32" src="" />
          <span class="username">Admin</span>
          <el-icon><ArrowDown /></el-icon>
        </div>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item>
              <el-icon><User /></el-icon>
              个人中心
            </el-dropdown-item>
            <el-dropdown-item divided>
              <el-icon><SwitchButton /></el-icon>
              退出登录
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </header>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import {
  Fold,
  Expand,
  Refresh,
  FullScreen,
  ArrowDown,
  User,
  SwitchButton,
} from '@element-plus/icons-vue'

const props = defineProps({
  collapsed: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['toggle-sidebar'])

const route = useRoute()

// 面包屑
const breadcrumbs = computed(() => {
  const items = [{ title: '首页', path: '/dashboard' }]
  if (route.meta.title && route.name !== 'Dashboard') {
    items.push({ title: route.meta.title, path: '' })
  }
  return items
})

// 切换侧边栏
const toggleSidebar = () => {
  emit('toggle-sidebar')
}

// 刷新页面
const handleRefresh = () => {
  window.location.reload()
}

// 全屏切换
const toggleFullscreen = () => {
  if (!document.fullscreenElement) {
    document.documentElement.requestFullscreen()
  } else {
    document.exitFullscreen()
  }
}
</script>

<style lang="scss" scoped>
.app-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;

  .collapse-btn {
    font-size: 20px;
    cursor: pointer;
    color: #606266;

    &:hover {
      color: #409eff;
    }
  }
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;

  .header-icon {
    font-size: 18px;
    cursor: pointer;
    color: #606266;
    padding: 8px;
    border-radius: 4px;

    &:hover {
      background-color: #f5f7fa;
      color: #409eff;
    }
  }

  .user-info {
    display: flex;
    align-items: center;
    gap: 8px;
    cursor: pointer;
    padding: 4px 8px;
    border-radius: 4px;

    &:hover {
      background-color: #f5f7fa;
    }

    .username {
      font-size: 14px;
      color: #606266;
    }
  }
}
</style>
