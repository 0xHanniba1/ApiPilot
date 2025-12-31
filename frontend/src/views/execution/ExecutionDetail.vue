<template>
  <div class="execution-detail" v-loading="loading">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <el-button text @click="$router.back()">
          <el-icon><ArrowLeft /></el-icon>
          返回
        </el-button>
        <h2 class="page-title">执行详情 #{{ executionId }}</h2>
        <el-tag :type="getStatusType(execution?.status)" size="large">
          {{ getStatusText(execution?.status) }}
        </el-tag>
      </div>
      <div class="header-right">
        <el-button @click="handleRerun" :loading="rerunning">
          <el-icon><RefreshRight /></el-icon>
          重新执行
        </el-button>
      </div>
    </div>

    <!-- 概览卡片 -->
    <div class="overview-section">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-label">通过率</div>
            <div class="stat-value">
              <el-progress
                type="circle"
                :percentage="passRate"
                :status="passRate === 100 ? 'success' : (passRate < 50 ? 'exception' : '')"
                :width="80"
              />
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-label">用例统计</div>
            <div class="stat-value case-stats">
              <div class="stat-item success">
                <span class="num">{{ execution?.passed_cases || 0 }}</span>
                <span class="label">通过</span>
              </div>
              <div class="stat-item danger">
                <span class="num">{{ execution?.failed_cases || 0 }}</span>
                <span class="label">失败</span>
              </div>
              <div class="stat-item info">
                <span class="num">{{ execution?.skipped_cases || 0 }}</span>
                <span class="label">跳过</span>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-label">执行耗时</div>
            <div class="stat-value">
              <span class="duration">{{ formatDuration(execution?.duration) }}</span>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-label">执行信息</div>
            <div class="stat-value execution-info">
              <div class="info-item">
                <span class="label">环境：</span>
                <span>{{ execution?.environment_name || '-' }}</span>
              </div>
              <div class="info-item">
                <span class="label">开始：</span>
                <span>{{ formatDate(execution?.started_at) }}</span>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 用例列表 -->
    <el-card class="cases-card">
      <template #header>
        <div class="card-header">
          <span>用例执行详情</span>
          <el-radio-group v-model="filterCaseStatus" size="small">
            <el-radio-button value="">全部</el-radio-button>
            <el-radio-button value="passed">通过</el-radio-button>
            <el-radio-button value="failed">失败</el-radio-button>
          </el-radio-group>
        </div>
      </template>

      <el-collapse v-model="expandedCases" accordion>
        <el-collapse-item
          v-for="caseResult in filteredCaseResults"
          :key="caseResult.id"
          :name="caseResult.id"
        >
          <template #title>
            <div class="case-title">
              <el-tag
                :type="getStatusType(caseResult.status)"
                size="small"
                class="status-tag"
              >
                {{ getStatusText(caseResult.status) }}
              </el-tag>
              <span class="case-name">{{ caseResult.case_name }}</span>
              <el-tag :class="['method-tag', caseResult.method]" size="small">
                {{ caseResult.method }}
              </el-tag>
              <span class="case-path">{{ caseResult.path }}</span>
              <span class="case-duration">{{ caseResult.response_time }}ms</span>
            </div>
          </template>

          <div class="case-detail">
            <!-- 请求信息 -->
            <div class="detail-section">
              <div class="section-title">请求信息</div>
              <div class="request-info">
                <div class="info-row">
                  <span class="label">URL：</span>
                  <span class="value">{{ caseResult.request_url }}</span>
                </div>
                <div v-if="caseResult.request_headers" class="info-row">
                  <span class="label">Headers：</span>
                  <pre class="code-block">{{ formatJson(caseResult.request_headers) }}</pre>
                </div>
                <div v-if="caseResult.request_body" class="info-row">
                  <span class="label">Body：</span>
                  <pre class="code-block">{{ formatJson(caseResult.request_body) }}</pre>
                </div>
              </div>
            </div>

            <!-- 响应信息 -->
            <div class="detail-section">
              <div class="section-title">
                响应信息
                <el-tag size="small" :type="getHttpStatusType(caseResult.status_code)">
                  {{ caseResult.status_code }}
                </el-tag>
              </div>
              <div class="response-info">
                <div v-if="caseResult.response_headers" class="info-row">
                  <span class="label">Headers：</span>
                  <pre class="code-block">{{ formatJson(caseResult.response_headers) }}</pre>
                </div>
                <div v-if="caseResult.response_body" class="info-row">
                  <span class="label">Body：</span>
                  <pre class="code-block response-body">{{ formatJson(caseResult.response_body) }}</pre>
                </div>
              </div>
            </div>

            <!-- 断言结果 -->
            <div v-if="caseResult.assertions && caseResult.assertions.length > 0" class="detail-section">
              <div class="section-title">断言结果</div>
              <div class="assertion-list">
                <div
                  v-for="(assertion, index) in caseResult.assertions"
                  :key="index"
                  :class="['assertion-item', { failed: !assertion.passed }]"
                >
                  <el-icon v-if="assertion.passed" class="icon success"><Check /></el-icon>
                  <el-icon v-else class="icon failed"><Close /></el-icon>
                  <div class="assertion-content">
                    <div class="assertion-name">
                      {{ assertion.name || `断言 ${index + 1}` }}
                    </div>
                    <div class="assertion-detail">
                      <span class="type">{{ getAssertionTypeText(assertion.type) }}</span>
                      <span v-if="assertion.expression" class="expression">{{ assertion.expression }}</span>
                      <span class="operator">{{ getOperatorText(assertion.operator) }}</span>
                      <span class="expected">{{ assertion.expected_value }}</span>
                    </div>
                    <div v-if="!assertion.passed" class="assertion-error">
                      实际值：{{ assertion.actual_value }}
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- 提取器结果 -->
            <div v-if="caseResult.extractors && caseResult.extractors.length > 0" class="detail-section">
              <div class="section-title">提取器结果</div>
              <div class="extractor-list">
                <div
                  v-for="(extractor, index) in caseResult.extractors"
                  :key="index"
                  class="extractor-item"
                >
                  <span class="var-name">${extractor.variable_name}}</span>
                  <span class="arrow">=</span>
                  <span class="var-value">{{ extractor.extracted_value || '(空)' }}</span>
                </div>
              </div>
            </div>

            <!-- 错误信息 -->
            <div v-if="caseResult.error_message" class="detail-section error-section">
              <div class="section-title">错误信息</div>
              <div class="error-message">{{ caseResult.error_message }}</div>
            </div>
          </div>
        </el-collapse-item>
      </el-collapse>

      <el-empty v-if="filteredCaseResults.length === 0" description="暂无数据" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft, RefreshRight, Check, Close } from '@element-plus/icons-vue'
import { getExecution, getExecutionDetails, executeSuite } from '@/api/execution'

const route = useRoute()
const router = useRouter()

const executionId = computed(() => route.params.id)

// 数据状态
const loading = ref(false)
const rerunning = ref(false)
const execution = ref(null)
const caseResults = ref([])
const expandedCases = ref([])
const filterCaseStatus = ref('')

// 计算通过率
const passRate = computed(() => {
  if (!execution.value || !execution.value.total_cases) return 0
  return Math.round((execution.value.passed_cases / execution.value.total_cases) * 100)
})

// 过滤用例结果
const filteredCaseResults = computed(() => {
  if (!filterCaseStatus.value) return caseResults.value
  return caseResults.value.filter(c => c.status === filterCaseStatus.value)
})

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

// 格式化 JSON
const formatJson = (data) => {
  if (!data) return ''
  if (typeof data === 'string') {
    try {
      return JSON.stringify(JSON.parse(data), null, 2)
    } catch {
      return data
    }
  }
  return JSON.stringify(data, null, 2)
}

// 状态样式
const getStatusType = (status) => {
  const types = {
    passed: 'success',
    failed: 'danger',
    running: 'warning',
    pending: 'info',
    skipped: 'info',
  }
  return types[status] || 'info'
}

const getStatusText = (status) => {
  const texts = {
    passed: '通过',
    failed: '失败',
    running: '运行中',
    pending: '等待中',
    skipped: '跳过',
  }
  return texts[status] || status
}

const getHttpStatusType = (code) => {
  if (code >= 200 && code < 300) return 'success'
  if (code >= 400) return 'danger'
  return 'warning'
}

// 断言类型文本
const getAssertionTypeText = (type) => {
  const texts = {
    status_code: '状态码',
    json_path: 'JSONPath',
    header: '响应头',
    response_time: '响应时间',
    contains: '包含',
  }
  return texts[type] || type
}

// 操作符文本
const getOperatorText = (operator) => {
  const texts = {
    eq: '等于',
    ne: '不等于',
    gt: '大于',
    lt: '小于',
    gte: '大于等于',
    lte: '小于等于',
    contains: '包含',
    not_contains: '不包含',
    regex: '正则匹配',
    exists: '存在',
    not_exists: '不存在',
  }
  return texts[operator] || operator
}

// 获取执行详情
const fetchExecution = async () => {
  loading.value = true
  try {
    const [execRes, detailsRes] = await Promise.all([
      getExecution(executionId.value),
      getExecutionDetails(executionId.value),
    ])
    execution.value = execRes.data
    caseResults.value = detailsRes.data || []

    // 自动展开失败的用例
    const failedCase = caseResults.value.find(c => c.status === 'failed')
    if (failedCase) {
      expandedCases.value = [failedCase.id]
    }
  } catch (error) {
    console.error('获取执行详情失败:', error)
    ElMessage.error('获取执行详情失败')
  } finally {
    loading.value = false
  }
}

// 重新执行
const handleRerun = async () => {
  if (!execution.value) return

  rerunning.value = true
  try {
    const res = await executeSuite({
      suite_id: execution.value.suite_id,
      environment_id: execution.value.environment_id,
    })
    ElMessage.success('已重新开始执行')
    if (res.data?.execution_id) {
      router.push(`/executions/${res.data.execution_id}`)
    }
  } catch (error) {
    console.error('执行失败:', error)
    ElMessage.error('执行失败')
  } finally {
    rerunning.value = false
  }
}

onMounted(() => {
  fetchExecution()
})
</script>

<style lang="scss" scoped>
.execution-detail {
  padding: 20px;

  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;

    .header-left {
      display: flex;
      align-items: center;
      gap: 12px;

      .page-title {
        font-size: 20px;
        font-weight: 600;
        color: #303133;
        margin: 0;
      }
    }
  }

  .overview-section {
    margin-bottom: 20px;

    .stat-card {
      text-align: center;

      .stat-label {
        color: #909399;
        font-size: 14px;
        margin-bottom: 12px;
      }

      .stat-value {
        .duration {
          font-size: 28px;
          font-weight: 600;
          color: #303133;
        }
      }

      .case-stats {
        display: flex;
        justify-content: center;
        gap: 24px;

        .stat-item {
          text-align: center;

          .num {
            display: block;
            font-size: 24px;
            font-weight: 600;
          }

          .label {
            font-size: 12px;
            color: #909399;
          }

          &.success .num {
            color: #67c23a;
          }

          &.danger .num {
            color: #f56c6c;
          }

          &.info .num {
            color: #909399;
          }
        }
      }

      .execution-info {
        text-align: left;

        .info-item {
          margin-bottom: 8px;
          font-size: 13px;

          .label {
            color: #909399;
          }
        }
      }
    }
  }

  .cases-card {
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .case-title {
      display: flex;
      align-items: center;
      gap: 12px;
      width: 100%;

      .status-tag {
        min-width: 50px;
      }

      .case-name {
        font-weight: 500;
        max-width: 300px;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }

      .case-path {
        color: #909399;
        font-size: 13px;
        flex: 1;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }

      .case-duration {
        color: #909399;
        font-size: 13px;
        margin-left: auto;
      }
    }

    .case-detail {
      padding: 16px;
      background: #fafafa;
      border-radius: 4px;

      .detail-section {
        margin-bottom: 20px;

        &:last-child {
          margin-bottom: 0;
        }

        .section-title {
          font-weight: 500;
          color: #303133;
          margin-bottom: 12px;
          display: flex;
          align-items: center;
          gap: 8px;
        }

        .info-row {
          margin-bottom: 8px;

          .label {
            color: #909399;
            margin-right: 8px;
          }

          .code-block {
            background: #f5f7fa;
            padding: 12px;
            border-radius: 4px;
            font-size: 12px;
            overflow-x: auto;
            margin-top: 4px;
            white-space: pre-wrap;
            word-break: break-all;

            &.response-body {
              max-height: 300px;
              overflow-y: auto;
            }
          }
        }
      }

      .assertion-list {
        .assertion-item {
          display: flex;
          align-items: flex-start;
          gap: 12px;
          padding: 12px;
          background: #f0f9eb;
          border-radius: 4px;
          margin-bottom: 8px;

          &.failed {
            background: #fef0f0;
          }

          .icon {
            font-size: 18px;
            margin-top: 2px;

            &.success {
              color: #67c23a;
            }

            &.failed {
              color: #f56c6c;
            }
          }

          .assertion-content {
            flex: 1;

            .assertion-name {
              font-weight: 500;
              margin-bottom: 4px;
            }

            .assertion-detail {
              font-size: 13px;
              color: #606266;

              .type,
              .expression,
              .operator,
              .expected {
                margin-right: 8px;
              }

              .expression {
                color: #e6a23c;
                font-family: monospace;
              }
            }

            .assertion-error {
              margin-top: 8px;
              color: #f56c6c;
              font-size: 13px;
            }
          }
        }
      }

      .extractor-list {
        .extractor-item {
          display: flex;
          align-items: center;
          gap: 8px;
          padding: 8px 12px;
          background: #fdf6ec;
          border-radius: 4px;
          margin-bottom: 8px;
          font-size: 13px;

          .var-name {
            color: #e6a23c;
            font-family: monospace;
          }

          .var-value {
            color: #67c23a;
            font-family: monospace;
          }
        }
      }

      .error-section {
        .error-message {
          background: #fef0f0;
          color: #f56c6c;
          padding: 12px;
          border-radius: 4px;
          font-size: 13px;
        }
      }
    }
  }

  .method-tag {
    font-weight: 600;
    text-transform: uppercase;

    &.GET {
      background-color: #e6f7ff;
      border-color: #91d5ff;
      color: #1890ff;
    }

    &.POST {
      background-color: #f6ffed;
      border-color: #b7eb8f;
      color: #52c41a;
    }

    &.PUT {
      background-color: #fff7e6;
      border-color: #ffd591;
      color: #fa8c16;
    }

    &.DELETE {
      background-color: #fff2f0;
      border-color: #ffccc7;
      color: #ff4d4f;
    }
  }
}
</style>
