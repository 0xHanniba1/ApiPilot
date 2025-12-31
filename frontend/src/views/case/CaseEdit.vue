<template>
  <div class="case-edit" v-loading="pageLoading">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <el-button text @click="goBack">
          <el-icon><ArrowLeft /></el-icon>
          返回
        </el-button>
        <el-input
          v-model="caseData.name"
          placeholder="用例名称"
          class="case-name-input"
          maxlength="200"
        />
      </div>
      <div class="header-right">
        <el-button @click="goBack">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">
          <el-icon><Check /></el-icon>
          保存
        </el-button>
      </div>
    </div>

    <!-- 主内容区 -->
    <div class="main-content">
      <el-row :gutter="20">
        <!-- 左侧：请求配置 -->
        <el-col :span="14">
          <el-card class="config-card">
            <template #header>
              <div class="card-header">
                <span>请求配置</span>
              </div>
            </template>

            <!-- 请求配置组件 -->
            <RequestConfig v-model="requestConfig" />

            <!-- 分隔线 -->
            <el-divider />

            <!-- 断言规则 -->
            <AssertionList v-model="caseData.assertions" />

            <!-- 分隔线 -->
            <el-divider />

            <!-- 提取器 -->
            <ExtractorList v-model="caseData.extractors" />

            <!-- 高级配置 -->
            <el-divider />
            <el-collapse>
              <el-collapse-item title="高级配置" name="advanced">
                <el-form label-width="100px" label-position="left">
                  <el-form-item label="超时时间">
                    <el-input-number
                      v-model="caseData.timeout"
                      :min="1"
                      :max="300"
                      :step="1"
                    />
                    <span class="form-hint">秒</span>
                  </el-form-item>
                  <el-form-item label="重试次数">
                    <el-input-number
                      v-model="caseData.retry_count"
                      :min="0"
                      :max="5"
                      :step="1"
                    />
                  </el-form-item>
                  <el-form-item label="启用状态">
                    <el-switch v-model="caseData.is_active" />
                  </el-form-item>
                  <el-form-item label="用例描述">
                    <el-input
                      v-model="caseData.description"
                      type="textarea"
                      :rows="3"
                      placeholder="用例描述（选填）"
                    />
                  </el-form-item>
                </el-form>
              </el-collapse-item>
            </el-collapse>
          </el-card>
        </el-col>

        <!-- 右侧：响应预览 -->
        <el-col :span="10">
          <el-card class="response-card">
            <template #header>
              <div class="card-header">
                <span>响应预览</span>
                <el-select
                  v-model="selectedEnvId"
                  placeholder="选择环境"
                  size="small"
                  style="width: 150px"
                >
                  <el-option
                    v-for="env in environments"
                    :key="env.id"
                    :label="env.name"
                    :value="env.id"
                  />
                </el-select>
              </div>
            </template>

            <ResponseViewer
              :response="response"
              :loading="executing"
              @send="handleExecute"
            />
          </el-card>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft, Check } from '@element-plus/icons-vue'
import RequestConfig from '@/components/case/RequestConfig.vue'
import AssertionList from '@/components/case/AssertionList.vue'
import ExtractorList from '@/components/case/ExtractorList.vue'
import ResponseViewer from '@/components/execution/ResponseViewer.vue'
import { getCase, createCase, updateCase } from '@/api/case'
import { debugExecute } from '@/api/execution'
import { getProjectEnvironments } from '@/api/project'

const route = useRoute()
const router = useRouter()

// 判断是新建还是编辑
const isNew = computed(() => route.params.id === 'new')
const caseId = computed(() => (isNew.value ? null : route.params.id))
const moduleId = computed(() => route.query.moduleId)

// 页面状态
const pageLoading = ref(false)
const saving = ref(false)
const executing = ref(false)

// 用例数据
const caseData = reactive({
  name: '',
  description: '',
  method: 'GET',
  path: '',
  headers: [],
  params: [],
  body_type: 'none',
  body_content: '',
  assertions: [],
  extractors: [],
  timeout: 30,
  retry_count: 0,
  is_active: true,
})

// 请求配置（用于 RequestConfig 组件）
const requestConfig = computed({
  get: () => ({
    method: caseData.method,
    path: caseData.path,
    params: caseData.params,
    headers: caseData.headers,
    body_type: caseData.body_type,
    body_content: caseData.body_content,
  }),
  set: (val) => {
    caseData.method = val.method
    caseData.path = val.path
    caseData.params = val.params
    caseData.headers = val.headers
    caseData.body_type = val.body_type
    caseData.body_content = val.body_content
  },
})

// 环境列表
const environments = ref([])
const selectedEnvId = ref(null)

// 响应数据
const response = ref(null)

// 获取用例详情
const fetchCase = async () => {
  if (isNew.value) return

  pageLoading.value = true
  try {
    const res = await getCase(caseId.value)
    const data = res.data
    Object.assign(caseData, {
      name: data.name || '',
      description: data.description || '',
      method: data.method || 'GET',
      path: data.path || '',
      headers: data.headers || [],
      params: data.params || [],
      body_type: data.body_type || 'none',
      body_content: data.body_content || '',
      assertions: data.assertions || [],
      extractors: data.extractors || [],
      timeout: data.timeout || 30,
      retry_count: data.retry_count || 0,
      is_active: data.is_active !== false,
    })
  } catch (error) {
    console.error('获取用例详情失败:', error)
    ElMessage.error('获取用例详情失败')
  } finally {
    pageLoading.value = false
  }
}

// 获取环境列表
const fetchEnvironments = async () => {
  // 从 URL 获取项目 ID
  let projectId = route.query.projectId

  if (!projectId) {
    // 尝试从 localStorage 获取最近的项目 ID
    projectId = localStorage.getItem('lastProjectId')
  }

  if (projectId) {
    try {
      const res = await getProjectEnvironments(projectId)
      environments.value = res.data || []
      // 默认选择第一个环境
      if (environments.value.length > 0) {
        const defaultEnv = environments.value.find(e => e.is_default) || environments.value[0]
        selectedEnvId.value = defaultEnv.id
      }
    } catch (error) {
      console.error('获取环境列表失败:', error)
    }
  }
}

// 保存用例
const handleSave = async () => {
  if (!caseData.name) {
    ElMessage.warning('请输入用例名称')
    return
  }

  if (!caseData.path) {
    ElMessage.warning('请输入请求路径')
    return
  }

  saving.value = true
  try {
    const payload = {
      name: caseData.name,
      description: caseData.description,
      method: caseData.method,
      path: caseData.path,
      headers: caseData.headers.filter(h => h.key),
      params: caseData.params.filter(p => p.key),
      body_type: caseData.body_type,
      body_content: caseData.body_content,
      assertions: caseData.assertions,
      extractors: caseData.extractors,
      timeout: caseData.timeout,
      retry_count: caseData.retry_count,
      is_active: caseData.is_active,
    }

    if (isNew.value) {
      if (!moduleId.value) {
        ElMessage.warning('缺少模块信息')
        return
      }
      await createCase(moduleId.value, payload)
      ElMessage.success('创建成功')
    } else {
      await updateCase(caseId.value, payload)
      ElMessage.success('保存成功')
    }

    goBack()
  } catch (error) {
    console.error('保存失败:', error)
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

// 执行调试
const handleExecute = async () => {
  if (!caseData.path) {
    ElMessage.warning('请输入请求路径')
    return
  }

  if (!selectedEnvId.value) {
    ElMessage.warning('请选择执行环境')
    return
  }

  executing.value = true
  response.value = null

  try {
    const payload = {
      environment_id: selectedEnvId.value,
      method: caseData.method,
      path: caseData.path,
      headers: caseData.headers.filter(h => h.key && h.enabled !== false),
      params: caseData.params.filter(p => p.key && p.enabled !== false),
      body_type: caseData.body_type,
      body_content: caseData.body_content,
    }

    const res = await debugExecute(payload)
    response.value = res.data
  } catch (error) {
    console.error('执行失败:', error)
    ElMessage.error('执行失败: ' + (error.message || '未知错误'))
  } finally {
    executing.value = false
  }
}

// 返回
const goBack = () => {
  router.back()
}

onMounted(() => {
  fetchCase()
  fetchEnvironments()
})
</script>

<style lang="scss" scoped>
.case-edit {
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

      .case-name-input {
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
      gap: 8px;
    }
  }

  .main-content {
    flex: 1;
    overflow: auto;

    .config-card,
    .response-card {
      height: calc(100vh - 160px);
      overflow: auto;

      .card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
      }
    }

    .config-card {
      :deep(.el-card__body) {
        padding-bottom: 40px;
      }

      .form-hint {
        margin-left: 8px;
        color: #909399;
      }
    }

    .response-card {
      :deep(.el-card__body) {
        height: calc(100% - 56px);
        display: flex;
        flex-direction: column;
      }
    }
  }
}
</style>
