<template>
  <div class="dashboard">
    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stat-row">
      <el-col :span="6">
        <div class="stat-card blue">
          <div class="stat-value">{{ stats.project_count }}</div>
          <div class="stat-label">项目总数</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card green">
          <div class="stat-value">{{ stats.case_count }}</div>
          <div class="stat-label">用例总数</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card orange">
          <div class="stat-value">{{ stats.today_execution_count }}</div>
          <div class="stat-label">今日执行</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card cyan">
          <div class="stat-value">{{ stats.overall_pass_rate }}%</div>
          <div class="stat-label">整体通过率</div>
        </div>
      </el-col>
    </el-row>

    <!-- 图表区域 -->
    <el-row :gutter="20" class="chart-row">
      <el-col :span="16">
        <el-card class="chart-card">
          <template #header>
            <span>执行趋势（近7天）</span>
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

    <!-- 快捷操作 -->
    <el-row :gutter="20">
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
import * as echarts from 'echarts'
import { getDashboardStats } from '@/api/stats'
import { Folder, Collection, Clock, Document } from '@element-plus/icons-vue'

const stats = ref({
  project_count: 0,
  case_count: 0,
  suite_count: 0,
  today_execution_count: 0,
  today_passed: 0,
  today_failed: 0,
  overall_pass_rate: 0,
})

const trendChartRef = ref(null)
const pieChartRef = ref(null)
let trendChart = null
let pieChart = null

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

// 更新图表
const updateCharts = () => {
  // 趋势图
  if (trendChart) {
    trendChart.setOption({
      tooltip: {
        trigger: 'axis',
      },
      legend: {
        data: ['通过', '失败'],
      },
      xAxis: {
        type: 'category',
        data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'],
      },
      yAxis: {
        type: 'value',
      },
      series: [
        {
          name: '通过',
          type: 'line',
          smooth: true,
          data: [5, 8, 6, 10, 12, 8, 15],
          itemStyle: { color: '#67c23a' },
          areaStyle: { color: 'rgba(103, 194, 58, 0.1)' },
        },
        {
          name: '失败',
          type: 'line',
          smooth: true,
          data: [1, 2, 1, 0, 3, 1, 2],
          itemStyle: { color: '#f56c6c' },
          areaStyle: { color: 'rgba(245, 108, 108, 0.1)' },
        },
      ],
    })
  }

  // 饼图
  if (pieChart) {
    const passed = stats.value.today_passed || 0
    const failed = stats.value.today_failed || 0

    pieChart.setOption({
      tooltip: {
        trigger: 'item',
      },
      legend: {
        bottom: 10,
      },
      series: [
        {
          type: 'pie',
          radius: ['40%', '70%'],
          avoidLabelOverlap: false,
          itemStyle: {
            borderRadius: 10,
            borderColor: '#fff',
            borderWidth: 2,
          },
          label: {
            show: true,
            formatter: '{b}: {c}',
          },
          data: [
            { value: passed, name: '通过', itemStyle: { color: '#67c23a' } },
            { value: failed, name: '失败', itemStyle: { color: '#f56c6c' } },
          ],
        },
      ],
    })
  }
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
  .stat-row {
    margin-bottom: 20px;
  }

  .chart-row {
    margin-bottom: 20px;
  }

  .chart-card {
    .chart-container {
      height: 300px;
    }
  }

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
</style>
