<template>
  <div class="extractor-list">
    <div class="section-header">
      <span class="section-title">变量提取器</span>
      <el-button type="primary" link size="small" @click="addExtractor">
        <el-icon><Plus /></el-icon>
        添加
      </el-button>
    </div>

    <div v-if="localExtractors.length === 0" class="empty-tip">
      <el-text type="info" size="small">暂无提取器，点击"添加"按钮创建</el-text>
    </div>

    <div v-else class="extractor-items">
      <div
        v-for="(extractor, index) in localExtractors"
        :key="index"
        class="extractor-item"
      >
        <div class="item-header">
          <span class="item-index">{{ index + 1 }}.</span>
          <el-input
            v-model="extractor.name"
            placeholder="提取器名称（选填）"
            size="small"
            style="width: 150px"
            @input="emitUpdate"
          />
          <el-button
            type="danger"
            link
            size="small"
            @click="removeExtractor(index)"
          >
            <el-icon><Delete /></el-icon>
          </el-button>
        </div>

        <div class="item-body">
          <!-- 提取来源 -->
          <el-select
            v-model="extractor.source"
            placeholder="来源"
            size="small"
            style="width: 120px"
            @change="emitUpdate"
          >
            <el-option label="响应体" value="body" />
            <el-option label="响应头" value="header" />
            <el-option label="Cookie" value="cookie" />
          </el-select>

          <!-- 提取表达式 -->
          <el-input
            v-model="extractor.expression"
            :placeholder="getExpressionPlaceholder(extractor)"
            size="small"
            style="width: 200px"
            @input="emitUpdate"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>

          <el-icon class="arrow-icon"><Right /></el-icon>

          <!-- 变量名 -->
          <el-input
            v-model="extractor.variable_name"
            placeholder="保存为变量"
            size="small"
            style="width: 140px"
            @input="emitUpdate"
          >
            <template #prefix>
              <span style="color: #e6a23c" v-text="'${'"></span>
            </template>
            <template #suffix>
              <span style="color: #e6a23c" v-text="'}'"></span>
            </template>
          </el-input>

          <!-- 默认值 -->
          <el-input
            v-model="extractor.default_value"
            placeholder="默认值（选填）"
            size="small"
            style="width: 120px"
            @input="emitUpdate"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { Plus, Delete, Right, Search } from '@element-plus/icons-vue'

const props = defineProps({
  modelValue: {
    type: Array,
    default: () => [],
  },
})

const emit = defineEmits(['update:modelValue'])

const localExtractors = ref([])

// 初始化
watch(() => props.modelValue, (val) => {
  localExtractors.value = val.map(item => ({ ...item }))
}, { immediate: true, deep: true })

// 添加提取器
const addExtractor = () => {
  localExtractors.value.push({
    name: '',
    source: 'body',
    expression: '',
    variable_name: '',
    default_value: '',
  })
  emitUpdate()
}

// 删除提取器
const removeExtractor = (index) => {
  localExtractors.value.splice(index, 1)
  emitUpdate()
}

// 获取表达式占位符
const getExpressionPlaceholder = (extractor) => {
  switch (extractor.source) {
    case 'body':
      return 'JSONPath 如 $.data.token'
    case 'header':
      return 'Header 名称'
    case 'cookie':
      return 'Cookie 名称'
    default:
      return '表达式'
  }
}

// 发送更新
const emitUpdate = () => {
  emit('update:modelValue', localExtractors.value.map(item => ({ ...item })))
}
</script>

<style lang="scss" scoped>
.extractor-list {
  .section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
    padding-bottom: 8px;
    border-bottom: 1px solid #ebeef5;

    .section-title {
      font-weight: 500;
      color: #303133;
    }
  }

  .empty-tip {
    padding: 20px;
    text-align: center;
  }

  .extractor-items {
    .extractor-item {
      padding: 12px;
      margin-bottom: 8px;
      background: #fdf6ec;
      border-radius: 4px;

      .item-header {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 8px;

        .item-index {
          font-weight: 500;
          color: #606266;
          min-width: 20px;
        }
      }

      .item-body {
        display: flex;
        align-items: center;
        gap: 8px;
        flex-wrap: wrap;

        .arrow-icon {
          color: #909399;
        }
      }
    }
  }
}
</style>
