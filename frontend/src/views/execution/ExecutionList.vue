<template>
  <div class="execution-list">
    <div class="page-header">
      <h2 class="page-title">执行历史</h2>
    </div>

    <!-- 筛选栏 -->
    <div class="filter-bar">
      <el-select
        v-model="filterProjectId"
        placeholder="选择项目"
        clearable
        style="width: 180px"
        @change="fetchExecutions"
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
        placeholder="执行状态"
        clearable
        style="width: 120px"
        @change="fetchExecutions"
      >
        <el-option label="通过" value="passed" />
        <el-option label="失败" value="failed" />
        <el-option label="运行中" value="running" />
        <el-option label="等待中" value="pending" />
      </el-select>

      <el-date-picker
        v-model="filterDateRange"
        type="daterange"
        range-separator="至"
        start-placeholder="开始日期"
        end-placeholder="结束日期"
        value-format="YYYY-MM-DD"
        style="width: 260px"
        @change="fetchExecutions"
      />

      <el-button @click="resetFilters">
        <el-icon><RefreshRight /></el-icon>
        重置
      </el-button>
    </div>

    <!-- 执行记录表格 -->
    <el-table :data="executions" v-loading="loading" stripe>
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column label="执行内容" min-width="200">
        <template #default="{ row }">
          <div class="execution-info">
            <el-icon v-if="row.suite_name"><Collection /></el-icon>
            <el-icon v-else><Document /></el-icon>
            <span>{{ row.suite_name || row.case_name || '-' }}</span>
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="project_name" label="项目" width="150" />
      <el-table-column prop="environment_name" label="环境" width="120" />
      <el-table-column label="状态" width="100" align="center">
        <template #default="{ row }">
          <el-tag :type="getStatusType(row.status)" size="default">
            {{ getStatusText(row.status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="通过率" width="150" align="center">
        <template #default="{ row }">
          <div v-if="row.total_cases > 0" class="pass-rate">
            <el-progress
              :percentage="Math.round((row.passed_cases / row.total_cases) * 100)"
              :status="row.passed_cases === row.total_cases ? 'success' : (row.failed_cases > 0 ? 'exception' : '')"
              :stroke-width="8"
            />
            <span class="rate-text">{{ row.passed_cases }}/{{ row.total_cases }}</span>
          </div>
          <span v-else class="text-muted">-</span>
        </template>
      </el-table-column>
      <el-table-column prop="duration" label="耗时" width="100" align="center">
        <template #default="{ row }">
          {{ formatDuration(row.duration) }}
        </template>
      </el-table-column>
      <el-table-column prop="started_at" label="开始时间" width="170">
        <template #default="{ row }">
          {{ formatDate(row.started_at) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="100" fixed="right">
        <template #default="{ row }">
          <el-button type="primary" link size="small" @click="goToDetail(row.id)">
            查看详情
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
        layout="total, prev, pager, next, jumper"
        @current-change="handlePageChange"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { RefreshRight, Collection, Document } from '@element-plus/icons-vue'
import { getExecutions } from '@/api/execution'
import { getProjects } from '@/api/project'

const router = useRouter()

// 数据状态
const executions = ref([])
const projects = ref([])
const loading = ref(false)
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)

// 筛选条件
const filterProjectId = ref(null)
const filterStatus = ref(null)
const filterDateRange = ref(null)

// 格式化日期
const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

// 格式化耗时
const formatDuration = (ms) => {
  if (!ms) return '-'
  if (ms < 1000) return `${ms}ms`
  if (ms < 60000) return `${(ms / 1000).toFixed(1)}s`
  return `${Math.floor(ms / 60000)}m ${Math.round((ms % 60000) / 1000)}s`
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

// 获取执行记录
const fetchExecutions = async () => {
  loading.value = true
  try {
    const params = {
      page: page.value,
      page_size: pageSize.value,
    }
    if (filterProjectId.value) {
      params.project_id = filterProjectId.value
    }
    if (filterStatus.value) {
      params.status = filterStatus.value
    }
    if (filterDateRange.value && filterDateRange.value.length === 2) {
      params.start_date = filterDateRange.value[0]
      params.end_date = filterDateRange.value[1]
    }

    const res = await getExecutions(params)
    executions.value = res.data.items || []
    total.value = res.data.total || 0
  } catch (error) {
    console.error('获取执行记录失败:', error)
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

// 重置筛选
const resetFilters = () => {
  filterProjectId.value = null
  filterStatus.value = null
  filterDateRange.value = null
  page.value = 1
  fetchExecutions()
}

// 分页
const handlePageChange = (newPage) => {
  page.value = newPage
  fetchExecutions()
}

// 跳转详情
const goToDetail = (id) => {
  router.push(`/executions/${id}`)
}

onMounted(() => {
  fetchProjects()
  fetchExecutions()
})
</script>

<style lang="scss" scoped>
.execution-list {
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

  .execution-info {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .pass-rate {
    display: flex;
    align-items: center;
    gap: 8px;

    .el-progress {
      flex: 1;
    }

    .rate-text {
      font-size: 12px;
      color: #606266;
      min-width: 40px;
    }
  }

  .text-muted {
    color: #909399;
  }

  .pagination {
    margin-top: 20px;
    display: flex;
    justify-content: flex-end;
  }
}
</style>
