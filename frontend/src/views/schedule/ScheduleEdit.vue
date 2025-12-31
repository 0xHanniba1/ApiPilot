<template>
  <div class="schedule-edit" v-loading="pageLoading">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <el-button text @click="goBack">
          <el-icon><ArrowLeft /></el-icon>
          返回
        </el-button>
        <el-input
          v-model="form.name"
          placeholder="任务名称"
          class="name-input"
          maxlength="100"
        />
      </div>
      <div class="header-right">
        <el-switch
          v-model="form.is_active"
          active-text="启用"
          inactive-text="禁用"
          style="margin-right: 16px;"
        />
        <el-button type="success" @click="handleRunNow" :loading="running">
          <el-icon><VideoPlay /></el-icon>
          立即执行
        </el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">
          <el-icon><Check /></el-icon>
          保存
        </el-button>
      </div>
    </div>

    <!-- 主内容区 -->
    <el-row :gutter="20" class="main-content">
      <!-- 左侧：基本配置 -->
      <el-col :span="14">
        <el-card class="config-card">
          <template #header>
            <span>基本配置</span>
          </template>

          <el-form
            ref="formRef"
            :model="form"
            :rules="rules"
            label-width="100px"
            class="config-form"
          >
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
                >
                  <div class="suite-option">
                    <span>{{ suite.name }}</span>
                    <el-tag size="small" type="info">{{ suite.case_count || 0 }} 用例</el-tag>
                  </div>
                </el-option>
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
                >
                  <div class="env-option">
                    <span>{{ env.name }}</span>
                    <el-tag v-if="env.is_default" size="small" type="success">默认</el-tag>
                  </div>
                </el-option>
              </el-select>
            </el-form-item>

            <el-form-item label="描述">
              <el-input
                v-model="form.description"
                type="textarea"
                :rows="3"
                placeholder="任务描述（选填）"
              />
            </el-form-item>
          </el-form>
        </el-card>

        <!-- Cron 表达式配置 -->
        <el-card class="cron-card">
          <template #header>
            <div class="card-header">
              <span>执行周期</span>
              <el-radio-group v-model="cronMode" size="small">
                <el-radio-button value="visual">可视化</el-radio-button>
                <el-radio-button value="manual">手动输入</el-radio-button>
              </el-radio-group>
            </div>
          </template>

          <!-- 可视化配置 -->
          <div v-if="cronMode === 'visual'" class="cron-visual">
            <el-form label-width="80px">
              <el-form-item label="执行频率">
                <el-select v-model="cronConfig.type" style="width: 150px" @change="updateCronExpression">
                  <el-option label="每天" value="daily" />
                  <el-option label="每周" value="weekly" />
                  <el-option label="每月" value="monthly" />
                  <el-option label="每小时" value="hourly" />
                  <el-option label="每隔" value="interval" />
                </el-select>
              </el-form-item>

              <!-- 每天 -->
              <el-form-item v-if="cronConfig.type === 'daily'" label="执行时间">
                <el-time-picker
                  v-model="cronConfig.time"
                  format="HH:mm"
                  value-format="HH:mm"
                  placeholder="选择时间"
                  @change="updateCronExpression"
                />
              </el-form-item>

              <!-- 每周 -->
              <template v-if="cronConfig.type === 'weekly'">
                <el-form-item label="星期">
                  <el-checkbox-group v-model="cronConfig.weekdays" @change="updateCronExpression">
                    <el-checkbox :value="1">周一</el-checkbox>
                    <el-checkbox :value="2">周二</el-checkbox>
                    <el-checkbox :value="3">周三</el-checkbox>
                    <el-checkbox :value="4">周四</el-checkbox>
                    <el-checkbox :value="5">周五</el-checkbox>
                    <el-checkbox :value="6">周六</el-checkbox>
                    <el-checkbox :value="0">周日</el-checkbox>
                  </el-checkbox-group>
                </el-form-item>
                <el-form-item label="执行时间">
                  <el-time-picker
                    v-model="cronConfig.time"
                    format="HH:mm"
                    value-format="HH:mm"
                    placeholder="选择时间"
                    @change="updateCronExpression"
                  />
                </el-form-item>
              </template>

              <!-- 每月 -->
              <template v-if="cronConfig.type === 'monthly'">
                <el-form-item label="日期">
                  <el-select v-model="cronConfig.day" style="width: 120px" @change="updateCronExpression">
                    <el-option v-for="d in 31" :key="d" :label="`${d}日`" :value="d" />
                  </el-select>
                </el-form-item>
                <el-form-item label="执行时间">
                  <el-time-picker
                    v-model="cronConfig.time"
                    format="HH:mm"
                    value-format="HH:mm"
                    placeholder="选择时间"
                    @change="updateCronExpression"
                  />
                </el-form-item>
              </template>

              <!-- 每小时 -->
              <el-form-item v-if="cronConfig.type === 'hourly'" label="分钟">
                <el-select v-model="cronConfig.minute" style="width: 120px" @change="updateCronExpression">
                  <el-option label="整点" :value="0" />
                  <el-option v-for="m in [15, 30, 45]" :key="m" :label="`${m}分`" :value="m" />
                </el-select>
              </el-form-item>

              <!-- 每隔 -->
              <el-form-item v-if="cronConfig.type === 'interval'" label="间隔">
                <div class="interval-config">
                  <el-input-number
                    v-model="cronConfig.interval"
                    :min="1"
                    :max="60"
                    style="width: 100px"
                    @change="updateCronExpression"
                  />
                  <el-select v-model="cronConfig.intervalUnit" style="width: 100px" @change="updateCronExpression">
                    <el-option label="分钟" value="minute" />
                    <el-option label="小时" value="hour" />
                  </el-select>
                </div>
              </el-form-item>
            </el-form>
          </div>

          <!-- 手动输入 -->
          <div v-else class="cron-manual">
            <el-input
              v-model="form.cron_expression"
              placeholder="Cron 表达式，如：0 0 8 * * *"
            />
            <div class="cron-help">
              <p>格式：秒 分 时 日 月 周</p>
              <div class="presets">
                <span class="preset-label">快捷选择：</span>
                <el-tag
                  v-for="preset in cronPresets"
                  :key="preset.value"
                  class="preset-tag"
                  effect="plain"
                  @click="form.cron_expression = preset.value"
                >
                  {{ preset.label }}
                </el-tag>
              </div>
            </div>
          </div>

          <!-- Cron 表达式预览 -->
          <div class="cron-preview">
            <div class="preview-label">Cron 表达式：</div>
            <code class="cron-code">{{ form.cron_expression || '未配置' }}</code>
            <div v-if="form.cron_expression" class="preview-desc">
              {{ getCronDescription(form.cron_expression) }}
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 右侧：通知配置和执行历史 -->
      <el-col :span="10">
        <!-- 通知配置 -->
        <el-card class="notify-card">
          <template #header>
            <div class="card-header">
              <span>通知配置</span>
              <el-switch v-model="form.notify_enabled" />
            </div>
          </template>

          <div v-if="form.notify_enabled" class="notify-config">
            <el-form label-width="80px">
              <el-form-item label="通知时机">
                <el-checkbox-group v-model="form.notify_on">
                  <el-checkbox value="always">每次执行</el-checkbox>
                  <el-checkbox value="failure">仅失败时</el-checkbox>
                  <el-checkbox value="success">仅成功时</el-checkbox>
                </el-checkbox-group>
              </el-form-item>

              <el-form-item label="通知方式">
                <el-checkbox-group v-model="form.notify_channels">
                  <el-checkbox value="email">邮件</el-checkbox>
                  <el-checkbox value="webhook">Webhook</el-checkbox>
                  <el-checkbox value="dingtalk">钉钉</el-checkbox>
                  <el-checkbox value="wecom">企业微信</el-checkbox>
                </el-checkbox-group>
              </el-form-item>

              <el-form-item v-if="form.notify_channels.includes('email')" label="邮件地址">
                <el-input
                  v-model="form.notify_emails"
                  placeholder="多个邮箱用逗号分隔"
                />
              </el-form-item>

              <el-form-item v-if="form.notify_channels.includes('webhook')" label="Webhook">
                <el-input
                  v-model="form.notify_webhook"
                  placeholder="Webhook URL"
                />
              </el-form-item>

              <el-form-item v-if="form.notify_channels.includes('dingtalk')" label="钉钉">
                <el-input
                  v-model="form.notify_dingtalk"
                  placeholder="钉钉机器人 Webhook"
                />
              </el-form-item>

              <el-form-item v-if="form.notify_channels.includes('wecom')" label="企微">
                <el-input
                  v-model="form.notify_wecom"
                  placeholder="企业微信机器人 Webhook"
                />
              </el-form-item>
            </el-form>
          </div>

          <el-empty v-else description="通知已禁用" :image-size="60" />
        </el-card>

        <!-- 执行历史 -->
        <el-card class="history-card">
          <template #header>
            <div class="card-header">
              <span>执行历史</span>
              <el-button type="primary" link size="small" @click="fetchHistory">
                <el-icon><Refresh /></el-icon>
                刷新
              </el-button>
            </div>
          </template>

          <div v-loading="historyLoading" class="history-list">
            <div v-if="history.length === 0" class="empty-history">
              <el-empty description="暂无执行记录" :image-size="60" />
            </div>
            <div
              v-for="item in history"
              :key="item.id"
              class="history-item"
              @click="goToExecution(item.execution_id)"
            >
              <div class="history-status">
                <el-tag :type="item.status === 'passed' ? 'success' : 'danger'" size="small">
                  {{ item.status === 'passed' ? '通过' : '失败' }}
                </el-tag>
              </div>
              <div class="history-info">
                <div class="history-time">{{ formatDate(item.executed_at) }}</div>
                <div class="history-stats">
                  通过 {{ item.passed_count || 0 }} / 失败 {{ item.failed_count || 0 }}
                </div>
              </div>
              <div class="history-duration">
                {{ formatDuration(item.duration) }}
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft, Check, VideoPlay, Refresh } from '@element-plus/icons-vue'
import {
  getSchedule,
  updateSchedule,
  runScheduleNow,
  getScheduleHistory,
} from '@/api/schedule'
import { getProjects, getProjectEnvironments } from '@/api/project'
import { getSuites } from '@/api/suite'

const route = useRoute()
const router = useRouter()

const scheduleId = computed(() => route.params.id)

// 页面状态
const pageLoading = ref(false)
const saving = ref(false)
const running = ref(false)
const historyLoading = ref(false)

// 数据
const projects = ref([])
const suites = ref([])
const environments = ref([])
const history = ref([])

// 表单数据
const formRef = ref(null)
const form = reactive({
  name: '',
  project_id: null,
  suite_id: null,
  environment_id: null,
  cron_expression: '',
  description: '',
  is_active: true,
  notify_enabled: false,
  notify_on: ['failure'],
  notify_channels: [],
  notify_emails: '',
  notify_webhook: '',
  notify_dingtalk: '',
  notify_wecom: '',
})

const rules = {
  project_id: [{ required: true, message: '请选择项目', trigger: 'change' }],
  suite_id: [{ required: true, message: '请选择测试集', trigger: 'change' }],
  environment_id: [{ required: true, message: '请选择执行环境', trigger: 'change' }],
}

// Cron 配置模式
const cronMode = ref('visual')
const cronConfig = reactive({
  type: 'daily',
  time: '08:00',
  weekdays: [1, 2, 3, 4, 5],
  day: 1,
  minute: 0,
  interval: 30,
  intervalUnit: 'minute',
})

// Cron 预设
const cronPresets = [
  { label: '每天 8:00', value: '0 0 8 * * *' },
  { label: '每天 12:00', value: '0 0 12 * * *' },
  { label: '每天 20:00', value: '0 0 20 * * *' },
  { label: '每小时', value: '0 0 * * * *' },
  { label: '每 30 分钟', value: '0 */30 * * * *' },
  { label: '工作日 8:00', value: '0 0 8 * * 1-5' },
]

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

// 解析 Cron 表达式描述
const getCronDescription = (cron) => {
  if (!cron) return ''
  const parts = cron.split(' ')
  if (parts.length !== 6) return '无效的 Cron 表达式'

  const [second, minute, hour, day, month, week] = parts

  if (second === '0' && minute === '0' && hour !== '*' && day === '*' && month === '*') {
    if (week === '*') return `每天 ${hour}:00 执行`
    if (week === '1-5') return `工作日 ${hour}:00 执行`
    const weekNames = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
    if (/^\d$/.test(week)) return `每${weekNames[parseInt(week)]} ${hour}:00 执行`
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

// 更新 Cron 表达式
const updateCronExpression = () => {
  const { type, time, weekdays, day, minute, interval, intervalUnit } = cronConfig

  let cron = ''
  const [hour, min] = (time || '08:00').split(':').map(Number)

  switch (type) {
    case 'daily':
      cron = `0 ${min} ${hour} * * *`
      break
    case 'weekly':
      if (weekdays.length === 0) {
        cron = `0 ${min} ${hour} * * *`
      } else {
        cron = `0 ${min} ${hour} * * ${weekdays.sort().join(',')}`
      }
      break
    case 'monthly':
      cron = `0 ${min} ${hour} ${day} * *`
      break
    case 'hourly':
      cron = `0 ${minute} * * * *`
      break
    case 'interval':
      if (intervalUnit === 'minute') {
        cron = `0 */${interval} * * * *`
      } else {
        cron = `0 0 */${interval} * * *`
      }
      break
  }

  form.cron_expression = cron
}

// 获取任务详情
const fetchSchedule = async () => {
  pageLoading.value = true
  try {
    const res = await getSchedule(scheduleId.value)
    const data = res.data

    form.name = data.name
    form.project_id = data.project_id
    form.suite_id = data.suite_id
    form.environment_id = data.environment_id
    form.cron_expression = data.cron_expression || ''
    form.description = data.description || ''
    form.is_active = data.is_active

    // 通知配置
    form.notify_enabled = data.notify_enabled || false
    form.notify_on = data.notify_on || ['failure']
    form.notify_channels = data.notify_channels || []
    form.notify_emails = data.notify_emails || ''
    form.notify_webhook = data.notify_webhook || ''
    form.notify_dingtalk = data.notify_dingtalk || ''
    form.notify_wecom = data.notify_wecom || ''

    // 加载关联数据
    if (data.project_id) {
      await loadProjectData(data.project_id)
    }

    // 解析 Cron 表达式到可视化配置
    parseCronExpression(data.cron_expression)
  } catch (error) {
    console.error('获取任务详情失败:', error)
    ElMessage.error('获取任务详情失败')
  } finally {
    pageLoading.value = false
  }
}

// 解析 Cron 表达式
const parseCronExpression = (cron) => {
  if (!cron) return

  const parts = cron.split(' ')
  if (parts.length !== 6) return

  const [, minute, hour, day, , week] = parts

  // 尝试匹配模式
  if (minute.startsWith('*/')) {
    cronConfig.type = 'interval'
    cronConfig.interval = parseInt(minute.replace('*/', ''))
    cronConfig.intervalUnit = 'minute'
  } else if (hour.startsWith('*/')) {
    cronConfig.type = 'interval'
    cronConfig.interval = parseInt(hour.replace('*/', ''))
    cronConfig.intervalUnit = 'hour'
  } else if (hour === '*') {
    cronConfig.type = 'hourly'
    cronConfig.minute = parseInt(minute) || 0
  } else if (day !== '*') {
    cronConfig.type = 'monthly'
    cronConfig.day = parseInt(day)
    cronConfig.time = `${hour.padStart(2, '0')}:${minute.padStart(2, '0')}`
  } else if (week !== '*') {
    cronConfig.type = 'weekly'
    cronConfig.weekdays = week.split(',').map(Number)
    cronConfig.time = `${hour.padStart(2, '0')}:${minute.padStart(2, '0')}`
  } else {
    cronConfig.type = 'daily'
    cronConfig.time = `${hour.padStart(2, '0')}:${minute.padStart(2, '0')}`
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

// 加载项目相关数据
const loadProjectData = async (projectId) => {
  try {
    const [suitesRes, envsRes] = await Promise.all([
      getSuites({ project_id: projectId, page: 1, page_size: 100 }),
      getProjectEnvironments(projectId),
    ])
    suites.value = suitesRes.data.items || []
    environments.value = envsRes.data || []
  } catch (error) {
    console.error('获取数据失败:', error)
  }
}

// 项目切换
const handleProjectChange = async (projectId) => {
  form.suite_id = null
  form.environment_id = null
  suites.value = []
  environments.value = []

  if (projectId) {
    await loadProjectData(projectId)

    // 设置默认环境
    if (environments.value.length > 0) {
      const defaultEnv = environments.value.find(e => e.is_default) || environments.value[0]
      form.environment_id = defaultEnv.id
    }
  }
}

// 获取执行历史
const fetchHistory = async () => {
  historyLoading.value = true
  try {
    const res = await getScheduleHistory(scheduleId.value, { limit: 10 })
    history.value = res.data || []
  } catch (error) {
    console.error('获取执行历史失败:', error)
  } finally {
    historyLoading.value = false
  }
}

// 保存
const handleSave = async () => {
  if (!form.name) {
    ElMessage.warning('请输入任务名称')
    return
  }

  try {
    await formRef.value.validate()
  } catch {
    return
  }

  saving.value = true
  try {
    await updateSchedule(scheduleId.value, {
      name: form.name,
      project_id: form.project_id,
      suite_id: form.suite_id,
      environment_id: form.environment_id,
      cron_expression: form.cron_expression,
      description: form.description,
      is_active: form.is_active,
      notify_enabled: form.notify_enabled,
      notify_on: form.notify_on,
      notify_channels: form.notify_channels,
      notify_emails: form.notify_emails,
      notify_webhook: form.notify_webhook,
      notify_dingtalk: form.notify_dingtalk,
      notify_wecom: form.notify_wecom,
    })

    ElMessage.success('保存成功')
  } catch (error) {
    console.error('保存失败:', error)
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

// 立即执行
const handleRunNow = async () => {
  running.value = true
  try {
    const res = await runScheduleNow(scheduleId.value)
    ElMessage.success('任务已开始执行')

    if (res.data?.execution_id) {
      router.push(`/executions/${res.data.execution_id}`)
    }
  } catch (error) {
    console.error('执行失败:', error)
    ElMessage.error('执行失败')
  } finally {
    running.value = false
  }
}

// 跳转执行详情
const goToExecution = (executionId) => {
  if (executionId) {
    router.push(`/executions/${executionId}`)
  }
}

// 返回
const goBack = () => {
  router.back()
}

// 监听 Cron 模式切换
watch(cronMode, (newMode) => {
  if (newMode === 'visual') {
    parseCronExpression(form.cron_expression)
  }
})

onMounted(() => {
  fetchProjects()
  fetchSchedule()
  fetchHistory()
})
</script>

<style lang="scss" scoped>
.schedule-edit {
  height: 100%;
  display: flex;
  flex-direction: column;
  padding: 20px;
  background: #f5f7fa;

  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 20px;
    background: #fff;
    border-radius: 4px;
    margin-bottom: 16px;

    .header-left {
      display: flex;
      align-items: center;
      gap: 12px;
      flex: 1;

      .name-input {
        max-width: 400px;

        :deep(.el-input__wrapper) {
          box-shadow: none;
          font-size: 16px;
          font-weight: 500;
        }
      }
    }

    .header-right {
      display: flex;
      align-items: center;
      gap: 8px;
    }
  }

  .main-content {
    flex: 1;
    overflow: auto;
  }

  .config-card,
  .cron-card,
  .notify-card,
  .history-card {
    margin-bottom: 16px;

    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
  }

  .config-form {
    padding: 8px 0;
  }

  .suite-option,
  .env-option {
    display: flex;
    justify-content: space-between;
    align-items: center;
    width: 100%;
  }

  .cron-visual {
    padding: 8px 0;

    .interval-config {
      display: flex;
      gap: 12px;
    }
  }

  .cron-manual {
    .cron-help {
      margin-top: 12px;
      font-size: 12px;
      color: #909399;

      p {
        margin: 0 0 8px;
      }

      .presets {
        display: flex;
        align-items: center;
        flex-wrap: wrap;
        gap: 8px;

        .preset-label {
          color: #606266;
        }

        .preset-tag {
          cursor: pointer;

          &:hover {
            color: #409eff;
            border-color: #409eff;
          }
        }
      }
    }
  }

  .cron-preview {
    margin-top: 16px;
    padding: 12px;
    background: #f5f7fa;
    border-radius: 4px;

    .preview-label {
      font-size: 12px;
      color: #909399;
      margin-bottom: 8px;
    }

    .cron-code {
      display: block;
      padding: 8px 12px;
      background: #fff;
      border-radius: 4px;
      font-family: monospace;
      font-size: 14px;
      color: #303133;
    }

    .preview-desc {
      margin-top: 8px;
      font-size: 13px;
      color: #67c23a;
    }
  }

  .notify-config {
    padding: 8px 0;
  }

  .history-list {
    max-height: 400px;
    overflow-y: auto;

    .empty-history {
      padding: 20px 0;
    }

    .history-item {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 12px;
      border-bottom: 1px solid #ebeef5;
      cursor: pointer;
      transition: background 0.2s;

      &:hover {
        background: #f5f7fa;
      }

      &:last-child {
        border-bottom: none;
      }

      .history-status {
        width: 60px;
      }

      .history-info {
        flex: 1;

        .history-time {
          font-size: 13px;
          color: #303133;
        }

        .history-stats {
          font-size: 12px;
          color: #909399;
          margin-top: 4px;
        }
      }

      .history-duration {
        font-size: 12px;
        color: #909399;
      }
    }
  }
}
</style>
