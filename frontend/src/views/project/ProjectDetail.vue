<template>
  <div class="page-container">
    <div class="page-header">
      <h2 class="page-title">{{ project?.name || '项目详情' }}</h2>
      <el-button @click="$router.back()">返回</el-button>
    </div>

    <el-row :gutter="20">
      <!-- 左侧模块树 -->
      <el-col :span="6">
        <el-card class="module-tree-card">
          <template #header>
            <div class="card-header">
              <span>模块</span>
              <el-button type="primary" link size="small">新建</el-button>
            </div>
          </template>
          <el-tree
            :data="modules"
            :props="{ label: 'name', children: 'children' }"
            default-expand-all
            highlight-current
            @node-click="handleModuleClick"
          >
            <template #default="{ node, data }">
              <span class="tree-node">
                <el-icon><Folder /></el-icon>
                <span>{{ node.label }}</span>
              </span>
            </template>
          </el-tree>
        </el-card>
      </el-col>

      <!-- 右侧用例列表 -->
      <el-col :span="18">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>用例列表</span>
              <el-button type="primary" size="small">新建用例</el-button>
            </div>
          </template>
          <el-table :data="cases" v-loading="loading" stripe>
            <el-table-column prop="name" label="用例名称" min-width="200" />
            <el-table-column prop="method" label="方法" width="100">
              <template #default="{ row }">
                <el-tag :class="['method-tag', row.method]" size="small">
                  {{ row.method }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="path" label="路径" min-width="200" show-overflow-tooltip />
            <el-table-column label="操作" width="180" fixed="right">
              <template #default="{ row }">
                <el-button type="primary" link @click="$router.push(`/cases/${row.id}/edit`)">
                  编辑
                </el-button>
                <el-button type="success" link>执行</el-button>
                <el-button type="danger" link>删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { Folder } from '@element-plus/icons-vue'
import { getProject, getProjectModules } from '@/api/project'
import { getModuleCases } from '@/api/case'

const route = useRoute()
const projectId = ref(route.params.id)

const project = ref(null)
const modules = ref([])
const cases = ref([])
const loading = ref(false)
const selectedModuleId = ref(null)

// 获取项目详情
const fetchProject = async () => {
  try {
    const res = await getProject(projectId.value)
    project.value = res.data
  } catch (error) {
    console.error('获取项目详情失败:', error)
  }
}

// 获取模块树
const fetchModules = async () => {
  try {
    const res = await getProjectModules(projectId.value)
    modules.value = res.data || []

    // 默认选中第一个模块
    if (modules.value.length > 0) {
      handleModuleClick(modules.value[0])
    }
  } catch (error) {
    console.error('获取模块列表失败:', error)
  }
}

// 点击模块
const handleModuleClick = async (module) => {
  selectedModuleId.value = module.id
  loading.value = true
  try {
    const res = await getModuleCases(module.id)
    cases.value = res.data.items || []
  } catch (error) {
    console.error('获取用例列表失败:', error)
    cases.value = []
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchProject()
  fetchModules()
})
</script>

<style lang="scss" scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.module-tree-card {
  height: calc(100vh - 200px);
  overflow: auto;
}

.tree-node {
  display: flex;
  align-items: center;
  gap: 6px;
}
</style>
