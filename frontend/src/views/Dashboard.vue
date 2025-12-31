<template>
  <div class="dashboard">
    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stat-row">
      <el-col :span="6">
        <div class="stat-card blue" @click="$router.push('/projects')">
          <div class="stat-icon">
            <el-icon><Folder /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.project_count }}</div>
            <div class="stat-label">项目总数</div>
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card green">
          <div class="stat-icon">
            <el-icon><Document /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.case_count }}</div>
            <div class="stat-label">用例总数</div>
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card orange" @click="$router.push('/executions')">
          <div class="stat-icon">
            <el-icon><VideoPlay /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.today_execution_count }}</div>
            <div class="stat-label">今日执行</div>
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card cyan">
          <div class="stat-icon">
            <el-icon><TrendCharts /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.overall_pass_rate }}%</div>
            <div class="stat-label">整体通过率</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 图表区域 -->
    <el-row :gutter="20" class="chart-row">
      <el-col :span="16">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>执行趋势（近7天）</span>
              <el-radio-group v-model="trendType" size="small" @change="updateTrendChart">
                <el-radio-button value="count">执行次数</el-radio-button>
                <el-radio-button value="rate">通过率</el-radio-button>
              </el-radio-group>
            </div>
          </template>
          <div ref="trendChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card class="chart-card">
          <template #header>
            <span>今日执行统计</span>
          </template>
          <div ref="pieChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 下半部分 -->
    <el-row :gutter="20" class="bottom-row">
      <!-- 最近执行记录 -->
      <el-col :span="14">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>最近执行记录</span>
              <el-button type="primary" link size="small" @click="$router.push('/executions')">
                查看全部
                <el-icon><ArrowRight /></el-icon>
              </el-button>
            </div>
          </template>
          <el-table :data="recentExecutions" stripe size="small" v-loading="loadingRecent">
            <el-table-column label="执行内容" min-width="160">
              <template #default="{ row }">
                <div class="execution-info">
                  <el-icon v-if="row.suite_name"><Collection /></el-icon>
                  <el-icon v-else><Document /></el-icon>
                  <span>{{ row.suite_name || row.case_name || '-' }}</span>
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="project_name" label="项目" width="120" />
            <el-table-column label="状态" width="80" align="center">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)" size="small">
                  {{ getStatusText(row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="通过率" width="100" align="center">
              <template #default="{ row }">
                <span v-if="row.total_cases > 0">
                  {{ Math.round((row.passed_cases / row.total_cases) * 100) }}%
                </span>
                <span v-else class="text-muted">-</span>
              </template>
            </el-table-column>
            <el-table-column prop="started_at" label="执行时间" width="150">
              <template #default="{ row }">
                {{ formatDate(row.started_at) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="80" align="center">
              <template #default="{ row }">
                <el-button type="primary" link size="small" @click="goToExecution(row.id)">
                  详情
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>

      <!-- 失败率 Top5 用例 -->
      <el-col :span="10">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>失败率 Top5 用例</span>
              <el-tooltip content="基于最近30天执行数据统计" placement="top">
                <el-icon class="help-icon"><QuestionFilled /></el-icon>
              </el-tooltip>
            </div>
          </template>
          <div v-loading="loadingTopFailures" class="top-failures">
            <div v-if="topFailures.length === 0" class="empty-tip">
              <el-empty description="暂无数据" :image-size="60" />
            </div>
            <div
              v-for="(item, index) in topFailures"
              :key="item.case_id"
              class="failure-item"
              @click="goToCase(item.case_id)"
            >
              <div class="failure-rank" :class="getRankClass(index)">
                {{ index + 1 }}
              </div>
              <div class="failure-info">
                <div class="failure-name">{{ item.case_name }}</div>
                <div class="failure-meta">
                  <span class="project-name">{{ item.project_name }}</span>
                  <span class="divider">|</span>
                  <span>执行 {{ item.total_count }} 次</span>
                </div>
              </div>
              <div class="failure-rate">
                <el-progress
                  type="circle"
                  :percentage="Math.round(item.failure_rate * 100)"
                  :width="50"
                  :stroke-width="4"
                  status="exception"
                />
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 快捷操作 -->
    <el-row :gutter="20" class="action-row">
      <el-col :span="24">
        <el-card>
          <template #header>
            <span>快捷操作</span>
          </template>
          <div class="quick-actions">
            <el-button type="primary" @click="$router.push('/projects')">
              <el-icon><Folder /></el-icon>
              项目管理
            </el-button>
            <el-button type="success" @click="$router.push('/suites')">
              <el-icon><Collection /></el-icon>
              测试集
            </el-button>
            <el-button type="warning" @click="$router.push('/schedules')">
              <el-icon><Clock /></el-icon>
              定时任务
            </el-button>
            <el-button type="info" @click="$router.push('/executions')">
              <el-icon><Document /></el-icon>
              执行历史
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import * as echarts from 'echarts'
import { getDashboardStats, getTopFailures } from '@/api/stats'
import { getExecutions } from '@/api/execution'
import {
  Folder,
  Collection,
  Clock,
  Document,
  VideoPlay,
  TrendCharts,
  ArrowRight,
  QuestionFilled,
} from '@element-plus/icons-vue'

const router = useRouter()

const stats = ref({
  project_count: 0,
  case_count: 0,
  suite_count: 0,
  today_execution_count: 0,
  today_passed: 0,
  today_failed: 0,
  overall_pass_rate: 0,
  trend_data: [],
})

const trendType = ref('count')
const recentExecutions = ref([])
const topFailures = ref([])
const loadingRecent = ref(false)
const loadingTopFailures = ref(false)

const trendChartRef = ref(null)
const pieChartRef = ref(null)
let trendChart = null
let pieChart = null

// 格式化日期
const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  const month = (date.getMonth() + 1).toString().padStart(2, '0')
  const day = date.getDate().toString().padStart(2, '0')
  const hour = date.getHours().toString().padStart(2, '0')
  const minute = date.getMinutes().toString().padStart(2, '0')
  return `${month}-${day} ${hour}:${minute}`
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

// 排名样式
const getRankClass = (index) => {
  if (index === 0) return 'rank-1'
  if (index === 1) return 'rank-2'
  if (index === 2) return 'rank-3'
  return ''
}

// 获取统计数据
const fetchStats = async () => {
  try {
    const res = await getDashboardStats()
    stats.value = res.data
    updateCharts()
  } catch (error) {
    console.error('获取统计数据失败:', error)
  }
}

// 获取最近执行记录
const fetchRecentExecutions = async () => {
  loadingRecent.value = true
  try {
    const res = await getExecutions({ page: 1, page_size: 8 })
    recentExecutions.value = res.data.items || []
  } catch (error) {
    console.error('获取执行记录失败:', error)
  } finally {
    loadingRecent.value = false
  }
}

// 获取失败率 Top5
const fetchTopFailures = async () => {
  loadingTopFailures.value = true
  try {
    const res = await getTopFailures({ limit: 5, days: 30 })
    topFailures.value = res.data || []
  } catch (error) {
    console.error('获取失败率数据失败:', error)
  } finally {
    loadingTopFailures.value = false
  }
}

// 更新图表
const updateCharts = () => {
  updateTrendChart()
  updatePieChart()
}

// 更新趋势图
const updateTrendChart = () => {
  if (!trendChart) return

  const trendData = stats.value.trend_data || []
  const dates = trendData.map(d => d.date)
  const passedData = trendData.map(d => d.passed || 0)
  const failedData = trendData.map(d => d.failed || 0)
  const rateData = trendData.map(d => {
    const total = (d.passed || 0) + (d.failed || 0)
    return total > 0 ? Math.round((d.passed / total) * 100) : 0
  })

  // 如果没有数据，使用模拟数据
  const displayDates = dates.length > 0 ? dates : getLast7Days()
  const displayPassed = passedData.length > 0 ? passedData : [5, 8, 6, 10, 12, 8, 15]
  const displayFailed = failedData.length > 0 ? failedData : [1, 2, 1, 0, 3, 1, 2]
  const displayRate = rateData.length > 0 ? rateData : [83, 80, 86, 100, 80, 89, 88]

  const option = trendType.value === 'count' ? {
    tooltip: {
      trigger: 'axis',
    },
    legend: {
      data: ['通过', '失败'],
      bottom: 0,
    },
    grid: {
      top: 20,
      right: 20,
      bottom: 40,
      left: 50,
    },
    xAxis: {
      type: 'category',
      data: displayDates,
      axisLine: { lineStyle: { color: '#dcdfe6' } },
      axisLabel: { color: '#606266' },
    },
    yAxis: {
      type: 'value',
      axisLine: { show: false },
      splitLine: { lineStyle: { color: '#ebeef5' } },
      axisLabel: { color: '#606266' },
    },
    series: [
      {
        name: '通过',
        type: 'line',
        smooth: true,
        data: displayPassed,
        itemStyle: { color: '#67c23a' },
        areaStyle: { color: 'rgba(103, 194, 58, 0.1)' },
      },
      {
        name: '失败',
        type: 'line',
        smooth: true,
        data: displayFailed,
        itemStyle: { color: '#f56c6c' },
        areaStyle: { color: 'rgba(245, 108, 108, 0.1)' },
      },
    ],
  } : {
    tooltip: {
      trigger: 'axis',
      formatter: '{b}: {c}%',
    },
    grid: {
      top: 20,
      right: 20,
      bottom: 30,
      left: 50,
    },
    xAxis: {
      type: 'category',
      data: displayDates,
      axisLine: { lineStyle: { color: '#dcdfe6' } },
      axisLabel: { color: '#606266' },
    },
    yAxis: {
      type: 'value',
      max: 100,
      axisLine: { show: false },
      splitLine: { lineStyle: { color: '#ebeef5' } },
      axisLabel: { color: '#606266', formatter: '{value}%' },
    },
    series: [
      {
        name: '通过率',
        type: 'line',
        smooth: true,
        data: displayRate,
        itemStyle: { color: '#409eff' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(64, 158, 255, 0.3)' },
            { offset: 1, color: 'rgba(64, 158, 255, 0.05)' },
          ]),
        },
        markLine: {
          silent: true,
          data: [{ yAxis: 90, lineStyle: { color: '#67c23a', type: 'dashed' } }],
          label: { formatter: '目标线 90%' },
        },
      },
    ],
  }

  trendChart.setOption(option, true)
}

// 获取最近7天日期
const getLast7Days = () => {
  const days = []
  for (let i = 6; i >= 0; i--) {
    const date = new Date()
    date.setDate(date.getDate() - i)
    days.push(`${date.getMonth() + 1}/${date.getDate()}`)
  }
  return days
}

// 更新饼图
const updatePieChart = () => {
  if (!pieChart) return

  const passed = stats.value.today_passed || 0
  const failed = stats.value.today_failed || 0
  const total = passed + failed

  pieChart.setOption({
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} ({d}%)',
    },
    legend: {
      bottom: 10,
    },
    series: [
      {
        type: 'pie',
        radius: ['40%', '70%'],
        center: ['50%', '45%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2,
        },
        label: {
          show: true,
          position: 'center',
          formatter: () => {
            if (total === 0) return '暂无数据'
            return `{total|${total}}\n{label|执行总数}`
          },
          rich: {
            total: {
              fontSize: 28,
              fontWeight: 'bold',
              color: '#303133',
            },
            label: {
              fontSize: 12,
              color: '#909399',
              padding: [5, 0, 0, 0],
            },
          },
        },
        emphasis: {
          label: {
            show: true,
          },
        },
        labelLine: {
          show: false,
        },
        data: total === 0 ? [
          { value: 1, name: '暂无数据', itemStyle: { color: '#dcdfe6' } },
        ] : [
          { value: passed, name: '通过', itemStyle: { color: '#67c23a' } },
          { value: failed, name: '失败', itemStyle: { color: '#f56c6c' } },
        ],
      },
    ],
  }, true)
}

// 跳转执行详情
const goToExecution = (id) => {
  router.push(`/executions/${id}`)
}

// 跳转用例详情
const goToCase = (id) => {
  router.push(`/cases/${id}/edit`)
}

// 初始化图表
const initCharts = () => {
  if (trendChartRef.value) {
    trendChart = echarts.init(trendChartRef.value)
  }
  if (pieChartRef.value) {
    pieChart = echarts.init(pieChartRef.value)
  }
}

// 窗口大小变化时重置图表
const handleResize = () => {
  trendChart?.resize()
  pieChart?.resize()
}

onMounted(() => {
  initCharts()
  fetchStats()
  fetchRecentExecutions()
  fetchTopFailures()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  trendChart?.dispose()
  pieChart?.dispose()
})
</script>

<style lang="scss" scoped>
.dashboard {
  padding: 20px;

  .stat-row {
    margin-bottom: 20px;
  }

  .stat-card {
    display: flex;
    align-items: center;
    padding: 20px;
    border-radius: 8px;
    color: #fff;
    cursor: pointer;
    transition: transform 0.2s, box-shadow 0.2s;

    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }

    &.blue {
      background: linear-gradient(135deg, #409eff 0%, #3a8ee6 100%);
    }

    &.green {
      background: linear-gradient(135deg, #67c23a 0%, #5daf34 100%);
    }

    &.orange {
      background: linear-gradient(135deg, #e6a23c 0%, #cf9236 100%);
    }

    &.cyan {
      background: linear-gradient(135deg, #00d1d1 0%, #00b8b8 100%);
    }

    .stat-icon {
      width: 50px;
      height: 50px;
      display: flex;
      align-items: center;
      justify-content: center;
      background: rgba(255, 255, 255, 0.2);
      border-radius: 12px;
      margin-right: 16px;

      .el-icon {
        font-size: 24px;
      }
    }

    .stat-content {
      .stat-value {
        font-size: 28px;
        font-weight: 600;
        line-height: 1.2;
      }

      .stat-label {
        font-size: 14px;
        opacity: 0.9;
        margin-top: 4px;
      }
    }
  }

  .chart-row {
    margin-bottom: 20px;
  }

  .chart-card {
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .chart-container {
      height: 280px;
    }
  }

  .bottom-row {
    margin-bottom: 20px;
  }

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;

    .help-icon {
      color: #909399;
      cursor: help;
    }
  }

  .execution-info {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .text-muted {
    color: #909399;
  }

  .top-failures {
    .empty-tip {
      padding: 20px 0;
    }

    .failure-item {
      display: flex;
      align-items: center;
      padding: 12px;
      border-radius: 8px;
      cursor: pointer;
      transition: background 0.2s;

      &:hover {
        background: #f5f7fa;
      }

      .failure-rank {
        width: 28px;
        height: 28px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 50%;
        background: #ebeef5;
        color: #909399;
        font-weight: 600;
        font-size: 14px;
        margin-right: 12px;

        &.rank-1 {
          background: #f56c6c;
          color: #fff;
        }

        &.rank-2 {
          background: #e6a23c;
          color: #fff;
        }

        &.rank-3 {
          background: #909399;
          color: #fff;
        }
      }

      .failure-info {
        flex: 1;
        min-width: 0;

        .failure-name {
          font-size: 14px;
          font-weight: 500;
          color: #303133;
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
        }

        .failure-meta {
          font-size: 12px;
          color: #909399;
          margin-top: 4px;

          .divider {
            margin: 0 8px;
          }
        }
      }

      .failure-rate {
        margin-left: 12px;
      }
    }
  }

  .action-row {
    .quick-actions {
      display: flex;
      gap: 16px;
      flex-wrap: wrap;

      .el-button {
        display: flex;
        align-items: center;
        gap: 8px;
      }
    }
  }
}
</style>
