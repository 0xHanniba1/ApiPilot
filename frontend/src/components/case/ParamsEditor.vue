<template>
  <div class="params-editor">
    <el-table :data="localParams" size="small" border>
      <el-table-column width="50" align="center">
        <template #default="{ row }">
          <el-checkbox v-model="row.enabled" @change="emitUpdate" />
        </template>
      </el-table-column>
      <el-table-column label="参数名" min-width="150">
        <template #default="{ row }">
          <el-input
            v-model="row.key"
            placeholder="参数名"
            @input="handleInput(row)"
          />
        </template>
      </el-table-column>
      <el-table-column label="参数值" min-width="200">
        <template #default="{ row }">
          <el-input
            v-model="row.value"
            placeholder="参数值，支持 {{变量}}"
            @input="emitUpdate"
          />
        </template>
      </el-table-column>
      <el-table-column label="描述" min-width="150">
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

// 本地数据，确保总有一个空行用于输入
const localParams = ref([])

// 初始化数据
const initData = () => {
  const data = props.modelValue.length > 0
    ? props.modelValue.map(item => ({ ...item, enabled: item.enabled !== false }))
    : []
  // 确保末尾有一个空行
  if (data.length === 0 || data[data.length - 1].key || data[data.length - 1].value) {
    data.push({ key: '', value: '', description: '', enabled: true })
  }
  localParams.value = data
}

watch(() => props.modelValue, initData, { immediate: true, deep: true })

// 处理输入，自动添加新行
const handleInput = (row) => {
  const lastRow = localParams.value[localParams.value.length - 1]
  if (row === lastRow && (row.key || row.value)) {
    localParams.value.push({ key: '', value: '', description: '', enabled: true })
  }
  emitUpdate()
}

// 删除行
const removeRow = (index) => {
  localParams.value.splice(index, 1)
  if (localParams.value.length === 0) {
    localParams.value.push({ key: '', value: '', description: '', enabled: true })
  }
  emitUpdate()
}

// 发送更新（过滤空行）
const emitUpdate = () => {
  const validParams = localParams.value.filter(item => item.key || item.value)
  emit('update:modelValue', validParams)
}
</script>

<style lang="scss" scoped>
.params-editor {
  :deep(.el-table) {
    .el-input__wrapper {
      box-shadow: none;
      background: transparent;
    }

    .el-table__cell {
      padding: 4px 0;
    }
  }
}
</style>
