<template>
  <aside class="app-sidebar" :class="{ collapsed }">
    <div class="sidebar-logo">
      <img src="/vite.svg" alt="Logo" class="logo-img" />
      <span v-show="!collapsed" class="logo-text">ApiPilot</span>
    </div>
    <el-menu
      :default-active="activeMenu"
      :collapse="collapsed"
      :collapse-transition="false"
      background-color="#304156"
      text-color="#bfcbd9"
      active-text-color="#409eff"
      router
    >
      <template v-for="item in menuItems" :key="item.path">
        <el-menu-item v-if="!item.hidden" :index="item.path">
          <el-icon>
            <component :is="item.icon" />
          </el-icon>
          <template #title>{{ item.title }}</template>
        </el-menu-item>
      </template>
    </el-menu>
  </aside>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import {
  HomeFilled,
  Folder,
  Collection,
  Clock,
  Document,
} from '@element-plus/icons-vue'

defineProps({
  collapsed: {
    type: Boolean,
    default: false,
  },
})

const route = useRoute()

// 菜单配置
const menuItems = [
  { path: '/dashboard', title: '首页', icon: HomeFilled },
  { path: '/projects', title: '项目管理', icon: Folder },
  { path: '/suites', title: '测试集', icon: Collection },
  { path: '/schedules', title: '定时任务', icon: Clock },
  { path: '/executions', title: '执行历史', icon: Document },
]

// 当前激活菜单
const activeMenu = computed(() => {
  const { path } = route
  // 处理详情页等子路由
  if (path.startsWith('/projects')) return '/projects'
  if (path.startsWith('/suites')) return '/suites'
  if (path.startsWith('/executions')) return '/executions'
  if (path.startsWith('/cases')) return '/projects'
  return path
})
</script>

<style lang="scss" scoped>
.app-sidebar {
  display: flex;
  flex-direction: column;

  .sidebar-logo {
    height: 60px;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 0 16px;
    background-color: #263445;

    .logo-img {
      width: 32px;
      height: 32px;
    }

    .logo-text {
      margin-left: 12px;
      font-size: 18px;
      font-weight: 600;
      color: #fff;
      white-space: nowrap;
    }
  }

  &.collapsed {
    .sidebar-logo {
      padding: 0;
      justify-content: center;
    }
  }

  :deep(.el-menu) {
    border-right: none;
    flex: 1;

    .el-menu-item {
      &:hover {
        background-color: #263445;
      }

      &.is-active {
        background-color: #409eff !important;
      }
    }
  }
}
</style>
