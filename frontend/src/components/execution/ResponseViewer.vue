<template>
  <div class="response-viewer">
    <!-- 响应状态栏 -->
    <div v-if="response" class="response-status">
      <el-tag
        :type="getStatusType(response.status_code)"
        size="default"
        class="status-tag"
      >
        {{ response.status_code }} {{ getStatusText(response.status_code) }}
      </el-tag>
      <span class="response-time">
        <el-icon><Timer /></el-icon>
        {{ response.response_time || 0 }} ms
      </span>
      <span v-if="response.response_size" class="response-size">
        <el-icon><Document /></el-icon>
        {{ formatSize(response.response_size) }}
      </span>
    </div>

    <!-- 空状态 -->
    <div v-if="!response" class="empty-state">
      <el-empty description="点击「发送请求」查看响应" :image-size="80">
        <el-button type="primary" :loading="loading" @click="$emit('send')">
          <el-icon><CaretRight /></el-icon>
          发送请求
        </el-button>
      </el-empty>
    </div>

    <!-- 响应内容 -->
    <div v-else class="response-content">
      <el-tabs v-model="activeTab" class="response-tabs">
        <!-- Body -->
        <el-tab-pane label="Body" name="body">
          <div class="body-toolbar">
            <el-radio-group v-model="bodyFormat" size="small">
              <el-radio-button value="pretty">格式化</el-radio-button>
              <el-radio-button value="raw">原始</el-radio-button>
            </el-radio-group>
            <el-button size="small" @click="copyBody">
              <el-icon><CopyDocument /></el-icon>
              复制
            </el-button>
          </div>
          <div ref="bodyEditorContainer" class="body-editor"></div>
        </el-tab-pane>

        <!-- Headers -->
        <el-tab-pane name="headers">
          <template #label>
            Headers
            <el-badge
              v-if="headersCount > 0"
              :value="headersCount"
              class="tab-badge"
            />
          </template>
          <el-table :data="responseHeaders" size="small" border max-height="400">
            <el-table-column prop="key" label="Header" width="200" />
            <el-table-column prop="value" label="Value" show-overflow-tooltip />
          </el-table>
        </el-tab-pane>

        <!-- Cookies -->
        <el-tab-pane name="cookies">
          <template #label>
            Cookies
            <el-badge
              v-if="cookiesCount > 0"
              :value="cookiesCount"
              class="tab-badge"
            />
          </template>
          <el-table :data="responseCookies" size="small" border max-height="400">
            <el-table-column prop="name" label="名称" width="150" />
            <el-table-column prop="value" label="值" show-overflow-tooltip />
            <el-table-column prop="domain" label="Domain" width="150" />
            <el-table-column prop="path" label="Path" width="100" />
          </el-table>
          <el-empty v-if="responseCookies.length === 0" description="无 Cookie" :image-size="60" />
        </el-tab-pane>
      </el-tabs>
    </div>

    <!-- 发送按钮（有响应时显示在底部） -->
    <div v-if="response" class="action-bar">
      <el-button type="primary" :loading="loading" @click="$emit('send')">
        <el-icon><CaretRight /></el-icon>
        重新发送
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onBeforeUnmount, nextTick } from 'vue'
import * as monaco from 'monaco-editor'
import { ElMessage } from 'element-plus'
import { Timer, Document, CaretRight, CopyDocument } from '@element-plus/icons-vue'

const props = defineProps({
  response: {
    type: Object,
    default: null,
  },
  loading: {
    type: Boolean,
    default: false,
  },
})

defineEmits(['send'])

const activeTab = ref('body')
const bodyFormat = ref('pretty')
const bodyEditorContainer = ref(null)
let bodyEditor = null

// 解析响应头
const responseHeaders = computed(() => {
  if (!props.response?.headers) return []
  const headers = props.response.headers
  if (typeof headers === 'object') {
    return Object.entries(headers).map(([key, value]) => ({ key, value }))
  }
  return []
})

const headersCount = computed(() => responseHeaders.value.length)

// 解析 Cookies
const responseCookies = computed(() => {
  if (!props.response?.cookies) return []
  const cookies = props.response.cookies
  if (Array.isArray(cookies)) {
    return cookies
  }
  if (typeof cookies === 'object') {
    return Object.entries(cookies).map(([name, value]) => ({
      name,
      value: typeof value === 'object' ? value.value : value,
      domain: typeof value === 'object' ? value.domain : '',
      path: typeof value === 'object' ? value.path : '/',
    }))
  }
  return []
})

const cookiesCount = computed(() => responseCookies.value.length)

// 获取状态码类型
const getStatusType = (code) => {
  if (code >= 200 && code < 300) return 'success'
  if (code >= 300 && code < 400) return 'warning'
  if (code >= 400) return 'danger'
  return 'info'
}

// 获取状态文本
const getStatusText = (code) => {
  const statusTexts = {
    200: 'OK',
    201: 'Created',
    204: 'No Content',
    301: 'Moved Permanently',
    302: 'Found',
    304: 'Not Modified',
    400: 'Bad Request',
    401: 'Unauthorized',
    403: 'Forbidden',
    404: 'Not Found',
    405: 'Method Not Allowed',
    500: 'Internal Server Error',
    502: 'Bad Gateway',
    503: 'Service Unavailable',
  }
  return statusTexts[code] || ''
}

// 格式化大小
const formatSize = (bytes) => {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(2)} KB`
  return `${(bytes / 1024 / 1024).toFixed(2)} MB`
}

// 初始化 Body 编辑器
const initBodyEditor = async () => {
  await nextTick()
  if (!bodyEditorContainer.value || !props.response) return

  if (bodyEditor) {
    bodyEditor.dispose()
  }

  let content = props.response.body || ''
  let language = 'plaintext'

  // 尝试格式化 JSON
  if (bodyFormat.value === 'pretty') {
    try {
      const parsed = JSON.parse(content)
      content = JSON.stringify(parsed, null, 2)
      language = 'json'
    } catch {
      // 不是 JSON，检查是否是 HTML/XML
      if (content.trim().startsWith('<')) {
        language = 'html'
      }
    }
  }

  bodyEditor = monaco.editor.create(bodyEditorContainer.value, {
    value: content,
    language,
    theme: 'vs',
    minimap: { enabled: false },
    lineNumbers: 'on',
    scrollBeyondLastLine: false,
    automaticLayout: true,
    readOnly: true,
    tabSize: 2,
    fontSize: 13,
    wordWrap: 'on',
    folding: true,
  })
}

// 复制 Body
const copyBody = async () => {
  try {
    const content = bodyEditor?.getValue() || props.response?.body || ''
    await navigator.clipboard.writeText(content)
    ElMessage.success('已复制到剪贴板')
  } catch {
    ElMessage.error('复制失败')
  }
}

// 监听响应变化
watch(() => props.response, () => {
  if (props.response) {
    nextTick(() => initBodyEditor())
  }
}, { deep: true })

// 监听格式切换
watch(bodyFormat, () => {
  if (props.response) {
    initBodyEditor()
  }
})

onMounted(() => {
  if (props.response) {
    initBodyEditor()
  }
})

onBeforeUnmount(() => {
  if (bodyEditor) {
    bodyEditor.dispose()
    bodyEditor = null
  }
})
</script>

<style lang="scss" scoped>
.response-viewer {
  height: 100%;
  display: flex;
  flex-direction: column;

  .response-status {
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 12px;
    background: #f5f7fa;
    border-radius: 4px;
    margin-bottom: 12px;

    .status-tag {
      font-weight: 600;
      font-size: 14px;
    }

    .response-time,
    .response-size {
      display: flex;
      align-items: center;
      gap: 4px;
      color: #606266;
      font-size: 13px;
    }
  }

  .empty-state {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .response-content {
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;

    .response-tabs {
      flex: 1;
      display: flex;
      flex-direction: column;

      :deep(.el-tabs__content) {
        flex: 1;
        overflow: auto;
      }

      .tab-badge {
        margin-left: 4px;

        :deep(.el-badge__content) {
          height: 16px;
          line-height: 16px;
          padding: 0 5px;
          font-size: 11px;
        }
      }
    }

    .body-toolbar {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 8px;
    }

    .body-editor {
      height: 350px;
      border: 1px solid #dcdfe6;
      border-radius: 4px;
    }
  }

  .action-bar {
    padding-top: 12px;
    border-top: 1px solid #ebeef5;
    text-align: center;
  }
}
</style>
