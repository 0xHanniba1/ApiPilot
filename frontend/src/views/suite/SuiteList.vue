<template>
  <div class="suite-list">
    <div class="page-header">
      <h2 class="page-title">测试集</h2>
      <el-button type="primary" @click="handleCreate">
        <el-icon><Plus /></el-icon>
        新建测试集
      </el-button>
    </div>

    <!-- 筛选栏 -->
    <div class="filter-bar">
      <el-select
        v-model="filterProjectId"
        placeholder="选择项目"
        clearable
        style="width: 200px"
        @change="fetchSuites"
      >
        <el-option
          v-for="project in projects"
          :key="project.id"
          :label="project.name"
          :value="project.id"
        />
      </el-select>
      <el-input
        v-model="searchKeyword"
        placeholder="搜索测试集名称"
        prefix-icon="Search"
        clearable
        style="width: 250px"
        @input="handleSearch"
      />
    </div>

    <!-- 测试集表格 -->
    <el-table :data="filteredSuites" v-loading="loading" stripe>
      <el-table-column prop="name" label="测试集名称" min-width="200">
        <template #default="{ row }">
          <el-link type="primary" @click="goToEdit(row.id)">
            {{ row.name }}
          </el-link>
        </template>
      </el-table-column>
      <el-table-column prop="project_name" label="所属项目" width="150" />
      <el-table-column prop="case_count" label="用例数" width="100" align="center">
        <template #default="{ row }">
          <el-tag type="info" size="small">{{ row.case_count || 0 }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="execution_mode" label="执行模式" width="120" align="center">
        <template #default="{ row }">
          <el-tag :type="row.execution_mode === 'parallel' ? 'warning' : 'success'" size="small">
            {{ row.execution_mode === 'parallel' ? '并行' : '顺序' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="last_run_status" label="上次执行" width="100" align="center">
        <template #default="{ row }">
          <el-tag
            v-if="row.last_run_status"
            :type="getStatusType(row.last_run_status)"
            size="small"
          >
            {{ getStatusText(row.last_run_status) }}
          </el-tag>
          <span v-else class="text-muted">-</span>
        </template>
      </el-table-column>
      <el-table-column prop="updated_at" label="更新时间" width="160">
        <template #default="{ row }">
          {{ formatDate(row.updated_at) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button type="primary" link size="small" @click="goToEdit(row.id)">
            编辑
          </el-button>
          <el-button type="success" link size="small" @click="handleExecute(row)">
            执行
          </el-button>
          <el-button type="danger" link size="small" @click="handleDelete(row)">
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <div v-if="total > pageSize" class="pagination">
      <el-pagination
        :current-page="page"
        :page-size="pageSize"
        :total="total"
        layout="total, prev, pager, next"
        @current-change="handlePageChange"
      />
    </div>

    <!-- 新建弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      title="新建测试集"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="所属项目" prop="project_id">
          <el-select v-model="form.project_id" placeholder="选择项目" style="width: 100%">
            <el-option
              v-for="project in projects"
              :key="project.id"
              :label="project.name"
              :value="project.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="测试集名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入测试集名称" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="3"
            placeholder="请输入描述（选填）"
          />
        </el-form-item>
        <el-form-item label="执行模式">
          <el-radio-group v-model="form.execution_mode">
            <el-radio value="sequential">顺序执行</el-radio>
            <el-radio value="parallel">并行执行</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">
          创建
        </el-button>
      </template>
    </el-dialog>

    <!-- 执行弹窗 -->
    <el-dialog
      v-model="executeDialogVisible"
      title="执行测试集"
      width="400px"
    >
      <el-form label-width="80px">
        <el-form-item label="选择环境">
          <el-select v-model="executeEnvId" placeholder="选择执行环境" style="width: 100%">
            <el-option
              v-for="env in executeEnvs"
              :key="env.id"
              :label="env.name"
              :value="env.id"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="executeDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="executing" @click="confirmExecute">
          开始执行
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { getSuites, createSuite, deleteSuite } from '@/api/suite'
import { executeSuite } from '@/api/execution'
import { getProjects, getProjectEnvironments } from '@/api/project'

const router = useRouter()

// 数据状态
const suites = ref([])
const projects = ref([])
const loading = ref(false)
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const filterProjectId = ref(null)
const searchKeyword = ref('')

// 弹窗状态
const dialogVisible = ref(false)
const submitting = ref(false)
const formRef = ref(null)

const form = reactive({
  project_id: null,
  name: '',
  description: '',
  execution_mode: 'sequential',
})

const rules = {
  project_id: [{ required: true, message: '请选择项目', trigger: 'change' }],
  name: [{ required: true, message: '请输入测试集名称', trigger: 'blur' }],
}

// 执行弹窗
const executeDialogVisible = ref(false)
const executing = ref(false)
const executeSuiteId = ref(null)
const executeEnvId = ref(null)
const executeEnvs = ref([])

// 过滤测试集
const filteredSuites = computed(() => {
  if (!searchKeyword.value) return suites.value
  const keyword = searchKeyword.value.toLowerCase()
  return suites.value.filter(s => s.name.toLowerCase().includes(keyword))
})

// 格式化日期
const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

// 状态样式
const getStatusType = (status) => {
  const types = {
    passed: 'success',
    failed: 'danger',
    running: 'warning',
    pending: 'info',
  }
  return types[status] || 'info'
}

const getStatusText = (status) => {
  const texts = {
    passed: '通过',
    failed: '失败',
    running: '运行中',
    pending: '等待中',
  }
  return texts[status] || status
}

// 获取数据
const fetchSuites = async () => {
  loading.value = true
  try {
    const params = { page: page.value, page_size: pageSize.value }
    if (filterProjectId.value) {
      params.project_id = filterProjectId.value
    }
    const res = await getSuites(params)
    suites.value = res.data.items || []
    total.value = res.data.total || 0
  } catch (error) {
    console.error('获取测试集列表失败:', error)
  } finally {
    loading.value = false
  }
}

const fetchProjects = async () => {
  try {
    const res = await getProjects({ page: 1, page_size: 100 })
    projects.value = res.data.items || []
  } catch (error) {
    console.error('获取项目列表失败:', error)
  }
}

// 搜索
const handleSearch = () => {
  // 前端过滤
}

// 分页
const handlePageChange = (newPage) => {
  page.value = newPage
  fetchSuites()
}

// 新建
const handleCreate = () => {
  form.project_id = filterProjectId.value || null
  form.name = ''
  form.description = ''
  form.execution_mode = 'sequential'
  dialogVisible.value = true
}

// 提交
const handleSubmit = async () => {
  try {
    await formRef.value.validate()
    submitting.value = true

    await createSuite(form)
    ElMessage.success('创建成功')
    dialogVisible.value = false
    fetchSuites()
  } catch (error) {
    if (error !== false) {
      console.error('创建失败:', error)
    }
  } finally {
    submitting.value = false
  }
}

// 跳转编辑
const goToEdit = (id) => {
  router.push(`/suites/${id}/edit`)
}

// 执行
const handleExecute = async (suite) => {
  executeSuiteId.value = suite.id

  // 获取项目环境
  try {
    const res = await getProjectEnvironments(suite.project_id)
    executeEnvs.value = res.data || []
    if (executeEnvs.value.length > 0) {
      const defaultEnv = executeEnvs.value.find(e => e.is_default) || executeEnvs.value[0]
      executeEnvId.value = defaultEnv.id
    }
    executeDialogVisible.value = true
  } catch (error) {
    ElMessage.error('获取环境列表失败')
  }
}

const confirmExecute = async () => {
  if (!executeEnvId.value) {
    ElMessage.warning('请选择执行环境')
    return
  }

  executing.value = true
  try {
    const res = await executeSuite({
      suite_id: executeSuiteId.value,
      environment_id: executeEnvId.value,
    })
    ElMessage.success('测试集已开始执行')
    executeDialogVisible.value = false

    // 跳转到执行详情
    if (res.data?.execution_id) {
      router.push(`/executions/${res.data.execution_id}`)
    }
  } catch (error) {
    console.error('执行失败:', error)
    ElMessage.error('执行失败')
  } finally {
    executing.value = false
  }
}

// 删除
const handleDelete = async (suite) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除测试集「${suite.name}」吗？`,
      '删除确认',
      { type: 'warning' }
    )
    await deleteSuite(suite.id)
    ElMessage.success('删除成功')
    fetchSuites()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
    }
  }
}

onMounted(() => {
  fetchProjects()
  fetchSuites()
})
</script>

<style lang="scss" scoped>
.suite-list {
  padding: 20px;

  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;

    .page-title {
      font-size: 20px;
      font-weight: 600;
      color: #303133;
      margin: 0;
    }
  }

  .filter-bar {
    display: flex;
    gap: 12px;
    margin-bottom: 20px;
  }

  .pagination {
    margin-top: 20px;
    display: flex;
    justify-content: flex-end;
  }

  .text-muted {
    color: #909399;
  }
}
</style>
