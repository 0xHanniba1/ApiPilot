<template>
  <div class="assertion-list">
    <div class="section-header">
      <span class="section-title">断言规则</span>
      <el-button type="primary" link size="small" @click="addAssertion">
        <el-icon><Plus /></el-icon>
        添加
      </el-button>
    </div>

    <div v-if="localAssertions.length === 0" class="empty-tip">
      <el-text type="info" size="small">暂无断言规则，点击"添加"按钮创建</el-text>
    </div>

    <div v-else class="assertion-items">
      <div
        v-for="(assertion, index) in localAssertions"
        :key="index"
        class="assertion-item"
      >
        <div class="item-header">
          <span class="item-index">{{ index + 1 }}.</span>
          <el-input
            v-model="assertion.name"
            placeholder="断言名称（选填）"
            size="small"
            style="width: 150px"
            @input="emitUpdate"
          />
          <el-button
            type="danger"
            link
            size="small"
            @click="removeAssertion(index)"
          >
            <el-icon><Delete /></el-icon>
          </el-button>
        </div>

        <div class="item-body">
          <!-- 断言类型 -->
          <el-select
            v-model="assertion.type"
            placeholder="断言类型"
            size="small"
            style="width: 140px"
            @change="handleTypeChange(assertion)"
          >
            <el-option label="状态码" value="status_code" />
            <el-option label="JSONPath" value="json_path" />
            <el-option label="响应头" value="header" />
            <el-option label="响应时间" value="response_time" />
            <el-option label="包含内容" value="contains" />
          </el-select>

          <!-- 表达式 -->
          <el-input
            v-if="assertion.type === 'json_path'"
            v-model="assertion.expression"
            placeholder="$.data.id"
            size="small"
            style="width: 160px"
            @input="emitUpdate"
          />
          <el-input
            v-else-if="assertion.type === 'header'"
            v-model="assertion.expression"
            placeholder="Header 名称"
            size="small"
            style="width: 160px"
            @input="emitUpdate"
          />

          <!-- 操作符 -->
          <el-select
            v-model="assertion.operator"
            placeholder="操作符"
            size="small"
            style="width: 120px"
            @change="emitUpdate"
          >
            <el-option label="等于" value="eq" />
            <el-option label="不等于" value="ne" />
            <el-option label="大于" value="gt" />
            <el-option label="小于" value="lt" />
            <el-option label="大于等于" value="gte" />
            <el-option label="小于等于" value="lte" />
            <el-option label="包含" value="contains" />
            <el-option label="不包含" value="not_contains" />
            <el-option label="正则匹配" value="regex" />
            <el-option label="存在" value="exists" />
            <el-option label="不存在" value="not_exists" />
          </el-select>

          <!-- 期望值 -->
          <el-input
            v-if="!['exists', 'not_exists'].includes(assertion.operator)"
            v-model="assertion.expected_value"
            :placeholder="getExpectedPlaceholder(assertion)"
            size="small"
            style="flex: 1; min-width: 120px"
            @input="emitUpdate"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { Plus, Delete } from '@element-plus/icons-vue'

const props = defineProps({
  modelValue: {
    type: Array,
    default: () => [],
  },
})

const emit = defineEmits(['update:modelValue'])

const localAssertions = ref([])

// 初始化
watch(() => props.modelValue, (val) => {
  localAssertions.value = val.map(item => ({ ...item }))
}, { immediate: true, deep: true })

// 添加断言
const addAssertion = () => {
  localAssertions.value.push({
    name: '',
    type: 'status_code',
    expression: '',
    operator: 'eq',
    expected_value: '200',
  })
  emitUpdate()
}

// 删除断言
const removeAssertion = (index) => {
  localAssertions.value.splice(index, 1)
  emitUpdate()
}

// 类型切换时设置默认值
const handleTypeChange = (assertion) => {
  if (assertion.type === 'status_code') {
    assertion.expression = ''
    assertion.expected_value = '200'
  } else if (assertion.type === 'response_time') {
    assertion.expression = ''
    assertion.operator = 'lt'
    assertion.expected_value = '1000'
  } else if (assertion.type === 'contains') {
    assertion.expression = ''
    assertion.operator = 'contains'
    assertion.expected_value = ''
  } else {
    assertion.expected_value = ''
  }
  emitUpdate()
}

// 获取期望值占位符
const getExpectedPlaceholder = (assertion) => {
  switch (assertion.type) {
    case 'status_code':
      return '200'
    case 'response_time':
      return '毫秒数'
    case 'json_path':
      return '期望值'
    case 'header':
      return 'Header 值'
    case 'contains':
      return '包含的内容'
    default:
      return '期望值'
  }
}

// 发送更新
const emitUpdate = () => {
  emit('update:modelValue', localAssertions.value.map(item => ({ ...item })))
}
</script>

<style lang="scss" scoped>
.assertion-list {
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

  .assertion-items {
    .assertion-item {
      padding: 12px;
      margin-bottom: 8px;
      background: #f5f7fa;
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
      }
    }
  }
}
</style>
