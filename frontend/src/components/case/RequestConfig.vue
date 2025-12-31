<template>
  <div class="request-config">
    <!-- 请求方法和 URL -->
    <div class="url-bar">
      <el-select v-model="localData.method" class="method-select" @change="emitUpdate">
        <el-option
          v-for="method in methods"
          :key="method"
          :label="method"
          :value="method"
        >
          <span :class="['method-option', method]">{{ method }}</span>
        </el-option>
      </el-select>
      <el-input
        v-model="localData.path"
        placeholder="请求路径，如 /api/users 或 {{base_url}}/api/users"
        class="url-input"
        @input="emitUpdate"
      >
        <template #prefix>
          <el-icon><Link /></el-icon>
        </template>
      </el-input>
    </div>

    <!-- Tabs: Params / Headers / Body -->
    <el-tabs v-model="activeTab" class="config-tabs">
      <el-tab-pane name="params">
        <template #label>
          <span>
            Params
            <el-badge
              v-if="paramsCount > 0"
              :value="paramsCount"
              class="tab-badge"
            />
          </span>
        </template>
        <ParamsEditor v-model="localData.params" @update:modelValue="emitUpdate" />
      </el-tab-pane>

      <el-tab-pane name="headers">
        <template #label>
          <span>
            Headers
            <el-badge
              v-if="headersCount > 0"
              :value="headersCount"
              class="tab-badge"
            />
          </span>
        </template>
        <HeadersEditor v-model="localData.headers" @update:modelValue="emitUpdate" />
      </el-tab-pane>

      <el-tab-pane name="body">
        <template #label>
          <span>
            Body
            <el-tag
              v-if="localData.body_type && localData.body_type !== 'none'"
              size="small"
              type="info"
              class="tab-tag"
            >
              {{ localData.body_type }}
            </el-tag>
          </span>
        </template>
        <BodyEditor
          :type="localData.body_type"
          :content="localData.body_content"
          @update:type="handleBodyTypeUpdate"
          @update:content="handleBodyContentUpdate"
        />
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { Link } from '@element-plus/icons-vue'
import ParamsEditor from './ParamsEditor.vue'
import HeadersEditor from './HeadersEditor.vue'
import BodyEditor from './BodyEditor.vue'

const props = defineProps({
  modelValue: {
    type: Object,
    default: () => ({
      method: 'GET',
      path: '',
      params: [],
      headers: [],
      body_type: 'none',
      body_content: '',
    }),
  },
})

const emit = defineEmits(['update:modelValue'])

const methods = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'HEAD', 'OPTIONS']
const activeTab = ref('params')

const localData = ref({ ...props.modelValue })

// 计算 badge 数量
const paramsCount = computed(() => {
  return (localData.value.params || []).filter(p => p.key).length
})

const headersCount = computed(() => {
  return (localData.value.headers || []).filter(h => h.key).length
})

// 监听外部变化
watch(() => props.modelValue, (val) => {
  localData.value = { ...val }
}, { deep: true })

// Body 更新处理
const handleBodyTypeUpdate = (type) => {
  localData.value.body_type = type
  emitUpdate()
}

const handleBodyContentUpdate = (content) => {
  localData.value.body_content = content
  emitUpdate()
}

// 发送更新
const emitUpdate = () => {
  emit('update:modelValue', { ...localData.value })
}
</script>

<style lang="scss" scoped>
.request-config {
  .url-bar {
    display: flex;
    gap: 8px;
    margin-bottom: 16px;

    .method-select {
      width: 120px;
      flex-shrink: 0;

      :deep(.el-input__inner) {
        font-weight: 600;
      }
    }

    .url-input {
      flex: 1;
    }
  }

  .method-option {
    font-weight: 600;

    &.GET {
      color: #1890ff;
    }
    &.POST {
      color: #52c41a;
    }
    &.PUT {
      color: #fa8c16;
    }
    &.PATCH {
      color: #faad14;
    }
    &.DELETE {
      color: #ff4d4f;
    }
    &.HEAD,
    &.OPTIONS {
      color: #722ed1;
    }
  }

  .config-tabs {
    :deep(.el-tabs__header) {
      margin-bottom: 12px;
    }

    .tab-badge {
      margin-left: 6px;

      :deep(.el-badge__content) {
        height: 16px;
        line-height: 16px;
        padding: 0 5px;
        font-size: 11px;
      }
    }

    .tab-tag {
      margin-left: 6px;
      text-transform: uppercase;
    }
  }
}
</style>
