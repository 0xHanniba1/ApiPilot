<template>
  <div class="schedule-list">
    <div class="page-header">
      <h2 class="page-title">定时任务</h2>
      <el-button type="primary" @click="handleCreate">
        <el-icon><Plus /></el-icon>
        新建任务
      </el-button>
    </div>

    <!-- 筛选栏 -->
    <div class="filter-bar">
      <el-select
        v-model="filterProjectId"
        placeholder="选择项目"
        clearable
        style="width: 180px"
        @change="fetchSchedules"
      >
        <el-option
          v-for="project in projects"
          :key="project.id"
          :label="project.name"
          :value="project.id"
        />
      </el-select>

      <el-select
        v-model="filterStatus"
        placeholder="任务状态"
        clearable
        style="width: 120px"
        @change="fetchSchedules"
      >
        <el-option label="启用" :value="true" />
        <el-option label="禁用" :value="false" />
      </el-select>

      <el-input
        v-model="searchKeyword"
        placeholder="搜索任务名称"
        prefix-icon="Search"
        clearable
        style="width: 200px"
        @input="handleSearch"
      />
    </div>

    <!-- 任务表格 -->
    <el-table :data="filteredSchedules" v-loading="loading" stripe>
      <el-table-column prop="name" label="任务名称" min-width="180">
        <template #default="{ row }">
          <el-link type="primary" @click="goToEdit(row.id)">
            {{ row.name }}
          </el-link>
        </template>
      </el-table-column>
      <el-table-column prop="project_name" label="项目" width="150" />
      <el-table-column prop="suite_name" label="测试集" width="150" />
      <el-table-column label="Cron 表达式" width="150">
        <template #default="{ row }">
          <el-tooltip :content="getCronDescription(row.cron_expression)" placement="top">
            <code class="cron-code">{{ row.cron_expression }}</code>
          </el-tooltip>
        </template>
      </el-table-column>
      <el-table-column label="状态" width="90" align="center">
        <template #default="{ row }">
          <el-switch
            :model-value="row.is_active"
            @change="handleToggle(row, $event)"
            :loading="row.toggling"
          />
        </template>
      </el-table-column>
      <el-table-column label="上次执行" width="160">
        <template #default="{ row }">
          <template v-if="row.last_run_at">
            <div class="last-run">
              <el-tag
                :type="row.last_run_status === 'passed' ? 'success' : 'danger'"
                size="small"
              >
                {{ row.last_run_status === 'passed' ? '通过' : '失败' }}
              </el-tag>
              <span class="run-time">{{ formatDate(row.last_run_at) }}</span>
            </div>
          </template>
          <span v-else class="text-muted">-</span>
        </template>
      </el-table-column>
      <el-table-column label="下次执行" width="160">
        <template #default="{ row }">
          <span v-if="row.is_active && row.next_run_at">
            {{ formatDate(row.next_run_at) }}
          </span>
          <span v-else class="text-muted">-</span>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="180" fixed="right">
        <template #default="{ row }">
          <el-button type="primary" link size="small" @click="goToEdit(row.id)">
            编辑
          </el-button>
          <el-button
            type="success"
            link
            size="small"
            :loading="row.running"
            @click="handleRunNow(row)"
          >
            立即执行
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
      title="新建定时任务"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="任务名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入任务名称" />
        </el-form-item>
        <el-form-item label="所属项目" prop="project_id">
          <el-select
            v-model="form.project_id"
            placeholder="选择项目"
            style="width: 100%"
            @change="handleProjectChange"
          >
            <el-option
              v-for="project in projects"
              :key="project.id"
              :label="project.name"
              :value="project.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="测试集" prop="suite_id">
          <el-select
            v-model="form.suite_id"
            placeholder="选择测试集"
            style="width: 100%"
            :disabled="!form.project_id"
          >
            <el-option
              v-for="suite in suites"
              :key="suite.id"
              :label="suite.name"
              :value="suite.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="执行环境" prop="environment_id">
          <el-select
            v-model="form.environment_id"
            placeholder="选择执行环境"
            style="width: 100%"
            :disabled="!form.project_id"
          >
            <el-option
              v-for="env in environments"
              :key="env.id"
              :label="env.name"
              :value="env.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="执行周期" prop="cron_expression">
          <div class="cron-input-wrapper">
            <el-input
              v-model="form.cron_expression"
              placeholder="Cron 表达式，如：0 0 8 * * *"
            />
            <el-dropdown trigger="click" @command="selectCronPreset">
              <el-button type="primary" link>
                常用配置
                <el-icon><ArrowDown /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="0 0 8 * * *">每天 8:00</el-dropdown-item>
                  <el-dropdown-item command="0 0 12 * * *">每天 12:00</el-dropdown-item>
                  <el-dropdown-item command="0 0 20 * * *">每天 20:00</el-dropdown-item>
                  <el-dropdown-item command="0 0 0 * * *">每天 0:00</el-dropdown-item>
                  <el-dropdown-item command="0 0 * * * *">每小时整点</el-dropdown-item>
                  <el-dropdown-item command="0 */30 * * * *">每 30 分钟</el-dropdown-item>
                  <el-dropdown-item command="0 0 8 * * 1-5">工作日 8:00</el-dropdown-item>
                  <el-dropdown-item command="0 0 10 * * 1">每周一 10:00</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
          <div v-if="form.cron_expression" class="cron-description">
            {{ getCronDescription(form.cron_expression) }}
          </div>
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="2"
            placeholder="请输入任务描述（选填）"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">
          创建
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, ArrowDown } from '@element-plus/icons-vue'
import {
  getSchedules,
  createSchedule,
  deleteSchedule,
  toggleSchedule,
  runScheduleNow,
} from '@/api/schedule'
import { getProjects, getProjectEnvironments } from '@/api/project'
import { getSuites } from '@/api/suite'

const router = useRouter()

// 数据状态
const schedules = ref([])
const projects = ref([])
const suites = ref([])
const environments = ref([])
const loading = ref(false)
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const filterProjectId = ref(null)
const filterStatus = ref(null)
const searchKeyword = ref('')

// 弹窗状态
const dialogVisible = ref(false)
const submitting = ref(false)
const formRef = ref(null)

const form = reactive({
  name: '',
  project_id: null,
  suite_id: null,
  environment_id: null,
  cron_expression: '',
  description: '',
})

const rules = {
  name: [{ required: true, message: '请输入任务名称', trigger: 'blur' }],
  project_id: [{ required: true, message: '请选择项目', trigger: 'change' }],
  suite_id: [{ required: true, message: '请选择测试集', trigger: 'change' }],
  environment_id: [{ required: true, message: '请选择执行环境', trigger: 'change' }],
  cron_expression: [
    { required: true, message: '请输入 Cron 表达式', trigger: 'blur' },
    { pattern: /^(\S+\s+){5}\S+$/, message: 'Cron 表达式格式不正确', trigger: 'blur' },
  ],
}

// 过滤任务
const filteredSchedules = computed(() => {
  if (!searchKeyword.value) return schedules.value
  const keyword = searchKeyword.value.toLowerCase()
  return schedules.value.filter(s => s.name.toLowerCase().includes(keyword))
})

// 格式化日期
const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

// 解析 Cron 表达式描述
const getCronDescription = (cron) => {
  if (!cron) return ''
  const parts = cron.split(' ')
  if (parts.length !== 6) return '无效的 Cron 表达式'

  const [second, minute, hour, day, month, week] = parts

  // 常见模式匹配
  if (second === '0' && minute === '0' && hour !== '*' && day === '*' && month === '*') {
    if (week === '*') return `每天 ${hour}:00 执行`
    if (week === '1-5') return `工作日 ${hour}:00 执行`
    if (week === '1') return `每周一 ${hour}:00 执行`
  }
  if (second === '0' && minute === '0' && hour === '*') return '每小时整点执行'
  if (second === '0' && minute.startsWith('*/')) {
    const interval = minute.replace('*/', '')
    return `每 ${interval} 分钟执行`
  }
  if (second === '0' && hour.startsWith('*/')) {
    const interval = hour.replace('*/', '')
    return `每 ${interval} 小时执行`
  }

  return `秒:${second} 分:${minute} 时:${hour} 日:${day} 月:${month} 周:${week}`
}

// 获取任务列表
const fetchSchedules = async () => {
  loading.value = true
  try {
    const params = { page: page.value, page_size: pageSize.value }
    if (filterProjectId.value) {
      params.project_id = filterProjectId.value
    }
    if (filterStatus.value !== null) {
      params.is_active = filterStatus.value
    }
    const res = await getSchedules(params)
    schedules.value = (res.data.items || []).map(item => ({
      ...item,
      toggling: false,
      running: false,
    }))
    total.value = res.data.total || 0
  } catch (error) {
    console.error('获取任务列表失败:', error)
  } finally {
    loading.value = false
  }
}

// 获取项目列表
const fetchProjects = async () => {
  try {
    const res = await getProjects({ page: 1, page_size: 100 })
    projects.value = res.data.items || []
  } catch (error) {
    console.error('获取项目列表失败:', error)
  }
}

// 项目切换时加载测试集和环境
const handleProjectChange = async (projectId) => {
  form.suite_id = null
  form.environment_id = null
  suites.value = []
  environments.value = []

  if (projectId) {
    try {
      const [suitesRes, envsRes] = await Promise.all([
        getSuites({ project_id: projectId, page: 1, page_size: 100 }),
        getProjectEnvironments(projectId),
      ])
      suites.value = suitesRes.data.items || []
      environments.value = envsRes.data || []

      // 设置默认环境
      if (environments.value.length > 0) {
        const defaultEnv = environments.value.find(e => e.is_default) || environments.value[0]
        form.environment_id = defaultEnv.id
      }
    } catch (error) {
      console.error('获取数据失败:', error)
    }
  }
}

// 搜索
const handleSearch = () => {
  // 前端过滤
}

// 分页
const handlePageChange = (newPage) => {
  page.value = newPage
  fetchSchedules()
}

// 新建任务
const handleCreate = () => {
  form.name = ''
  form.project_id = filterProjectId.value || null
  form.suite_id = null
  form.environment_id = null
  form.cron_expression = ''
  form.description = ''
  suites.value = []
  environments.value = []

  if (form.project_id) {
    handleProjectChange(form.project_id)
  }

  dialogVisible.value = true
}

// 选择 Cron 预设
const selectCronPreset = (cron) => {
  form.cron_expression = cron
}

// 提交创建
const handleSubmit = async () => {
  try {
    await formRef.value.validate()
    submitting.value = true

    await createSchedule(form)
    ElMessage.success('创建成功')
    dialogVisible.value = false
    fetchSchedules()
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
  router.push(`/schedules/${id}/edit`)
}

// 切换启用状态
const handleToggle = async (row, value) => {
  row.toggling = true
  try {
    await toggleSchedule(row.id, value)
    row.is_active = value
    ElMessage.success(value ? '已启用' : '已禁用')
  } catch (error) {
    console.error('操作失败:', error)
    ElMessage.error('操作失败')
  } finally {
    row.toggling = false
  }
}

// 立即执行
const handleRunNow = async (row) => {
  row.running = true
  try {
    const res = await runScheduleNow(row.id)
    ElMessage.success('任务已开始执行')

    // 跳转到执行详情
    if (res.data?.execution_id) {
      router.push(`/executions/${res.data.execution_id}`)
    }
  } catch (error) {
    console.error('执行失败:', error)
    ElMessage.error('执行失败')
  } finally {
    row.running = false
  }
}

// 删除任务
const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除定时任务「${row.name}」吗？`,
      '删除确认',
      { type: 'warning' }
    )
    await deleteSchedule(row.id)
    ElMessage.success('删除成功')
    fetchSchedules()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
    }
  }
}

onMounted(() => {
  fetchProjects()
  fetchSchedules()
})
</script>

<style lang="scss" scoped>
.schedule-list {
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
    flex-wrap: wrap;
  }

  .cron-code {
    padding: 4px 8px;
    background: #f5f7fa;
    border-radius: 4px;
    font-size: 12px;
    color: #606266;
  }

  .last-run {
    display: flex;
    flex-direction: column;
    gap: 4px;

    .run-time {
      font-size: 12px;
      color: #909399;
    }
  }

  .cron-input-wrapper {
    display: flex;
    gap: 12px;
    align-items: center;
    width: 100%;

    .el-input {
      flex: 1;
    }
  }

  .cron-description {
    margin-top: 8px;
    font-size: 12px;
    color: #67c23a;
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
