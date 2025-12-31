<template>
  <div class="headers-editor">
    <el-table :data="localHeaders" size="small" border>
      <el-table-column width="50" align="center">
        <template #default="{ row }">
          <el-checkbox v-model="row.enabled" @change="emitUpdate" />
        </template>
      </el-table-column>
      <el-table-column label="Header 名" min-width="180">
        <template #default="{ row }">
          <el-autocomplete
            v-model="row.key"
            :fetch-suggestions="queryHeaders"
            placeholder="Header 名"
            style="width: 100%"
            @input="handleInput(row)"
            @select="emitUpdate"
          />
        </template>
      </el-table-column>
      <el-table-column label="值" min-width="200">
        <template #default="{ row }">
          <el-input
            v-model="row.value"
            placeholder="值，支持 {{变量}}"
            @input="emitUpdate"
          />
        </template>
      </el-table-column>
      <el-table-column label="描述" min-width="120">
        <template #default="{ row }">
          <el-input
            v-model="row.description"
            placeholder="描述（选填）"
            @input="emitUpdate"
          />
        </template>
      </el-table-column>
      <el-table-column width="60" align="center">
        <template #default="{ row, $index }">
          <el-button
            v-if="row.key || row.value"
            type="danger"
            link
            size="small"
            @click="removeRow($index)"
          >
            <el-icon><Delete /></el-icon>
          </el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { Delete } from '@element-plus/icons-vue'

const props = defineProps({
  modelValue: {
    type: Array,
    default: () => [],
  },
})

const emit = defineEmits(['update:modelValue'])

// 常用 Headers 建议
const commonHeaders = [
  'Content-Type',
  'Authorization',
  'Accept',
  'Accept-Language',
  'Accept-Encoding',
  'Cache-Control',
  'Cookie',
  'User-Agent',
  'Referer',
  'Origin',
  'X-Requested-With',
  'X-Api-Key',
  'X-Auth-Token',
]

const localHeaders = ref([])

const initData = () => {
  const data = props.modelValue.length > 0
    ? props.modelValue.map(item => ({ ...item, enabled: item.enabled !== false }))
    : []
  if (data.length === 0 || data[data.length - 1].key || data[data.length - 1].value) {
    data.push({ key: '', value: '', description: '', enabled: true })
  }
  localHeaders.value = data
}

watch(() => props.modelValue, initData, { immediate: true, deep: true })

// Header 自动补全
const queryHeaders = (queryString, cb) => {
  const results = queryString
    ? commonHeaders.filter(h => h.toLowerCase().includes(queryString.toLowerCase()))
    : commonHeaders
  cb(results.map(value => ({ value })))
}

const handleInput = (row) => {
  const lastRow = localHeaders.value[localHeaders.value.length - 1]
  if (row === lastRow && (row.key || row.value)) {
    localHeaders.value.push({ key: '', value: '', description: '', enabled: true })
  }
  emitUpdate()
}

const removeRow = (index) => {
  localHeaders.value.splice(index, 1)
  if (localHeaders.value.length === 0) {
    localHeaders.value.push({ key: '', value: '', description: '', enabled: true })
  }
  emitUpdate()
}

const emitUpdate = () => {
  const validHeaders = localHeaders.value.filter(item => item.key || item.value)
  emit('update:modelValue', validHeaders)
}
</script>

<style lang="scss" scoped>
.headers-editor {
  :deep(.el-table) {
    .el-input__wrapper,
    .el-autocomplete {
      box-shadow: none;
      background: transparent;
    }

    .el-table__cell {
      padding: 4px 0;
    }
  }
}
</style>
