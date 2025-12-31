<template>
  <div class="body-editor">
    <!-- Body 类型选择 -->
    <div class="body-type-selector">
      <el-radio-group v-model="bodyType" @change="handleTypeChange">
        <el-radio-button value="none">none</el-radio-button>
        <el-radio-button value="json">JSON</el-radio-button>
        <el-radio-button value="form">x-www-form-urlencoded</el-radio-button>
        <el-radio-button value="form-data">form-data</el-radio-button>
        <el-radio-button value="raw">raw</el-radio-button>
      </el-radio-group>
    </div>

    <!-- Body 内容 -->
    <div class="body-content">
      <!-- none -->
      <div v-if="bodyType === 'none'" class="body-none">
        <el-empty description="该请求没有 Body" :image-size="60" />
      </div>

      <!-- JSON / Raw -->
      <div v-else-if="bodyType === 'json' || bodyType === 'raw'" class="body-code">
        <div ref="editorContainer" class="monaco-container"></div>
      </div>

      <!-- Form / Form-data -->
      <div v-else-if="bodyType === 'form' || bodyType === 'form-data'" class="body-form">
        <el-table :data="formData" size="small" border>
          <el-table-column width="50" align="center">
            <template #default="{ row }">
              <el-checkbox v-model="row.enabled" @change="emitFormUpdate" />
            </template>
          </el-table-column>
          <el-table-column v-if="bodyType === 'form-data'" label="类型" width="100">
            <template #default="{ row }">
              <el-select v-model="row.type" size="small" @change="emitFormUpdate">
                <el-option label="Text" value="text" />
                <el-option label="File" value="file" />
              </el-select>
            </template>
          </el-table-column>
          <el-table-column label="字段名" min-width="150">
            <template #default="{ row }">
              <el-input
                v-model="row.key"
                placeholder="字段名"
                @input="handleFormInput(row)"
              />
            </template>
          </el-table-column>
          <el-table-column label="值" min-width="200">
            <template #default="{ row }">
              <template v-if="row.type === 'file'">
                <el-input v-model="row.value" placeholder="文件路径" @input="emitFormUpdate" />
              </template>
              <template v-else>
                <el-input v-model="row.value" placeholder="值，支持 {{变量}}" @input="emitFormUpdate" />
              </template>
            </template>
          </el-table-column>
          <el-table-column width="60" align="center">
            <template #default="{ row, $index }">
              <el-button
                v-if="row.key || row.value"
                type="danger"
                link
                size="small"
                @click="removeFormRow($index)"
              >
                <el-icon><Delete /></el-icon>
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onBeforeUnmount, nextTick } from 'vue'
import * as monaco from 'monaco-editor'
import { Delete } from '@element-plus/icons-vue'

const props = defineProps({
  type: {
    type: String,
    default: 'none',
  },
  content: {
    type: String,
    default: '',
  },
})

const emit = defineEmits(['update:type', 'update:content'])

const bodyType = ref(props.type || 'none')
const editorContainer = ref(null)
let editor = null

// Form 数据
const formData = ref([])

// 初始化 Form 数据
const initFormData = () => {
  if (bodyType.value === 'form' || bodyType.value === 'form-data') {
    try {
      const parsed = props.content ? JSON.parse(props.content) : []
      formData.value = Array.isArray(parsed) ? parsed.map(item => ({
        ...item,
        enabled: item.enabled !== false,
        type: item.type || 'text',
      })) : []
    } catch {
      formData.value = []
    }
    // 确保有空行
    if (formData.value.length === 0 || formData.value[formData.value.length - 1].key) {
      formData.value.push({ key: '', value: '', type: 'text', enabled: true })
    }
  }
}

// 初始化 Monaco Editor
const initEditor = async () => {
  await nextTick()
  if (!editorContainer.value) return

  if (editor) {
    editor.dispose()
  }

  const language = bodyType.value === 'json' ? 'json' : 'plaintext'

  editor = monaco.editor.create(editorContainer.value, {
    value: props.content || (bodyType.value === 'json' ? '{\n  \n}' : ''),
    language,
    theme: 'vs',
    minimap: { enabled: false },
    lineNumbers: 'on',
    scrollBeyondLastLine: false,
    automaticLayout: true,
    tabSize: 2,
    fontSize: 13,
    wordWrap: 'on',
    folding: true,
    renderWhitespace: 'selection',
  })

  editor.onDidChangeModelContent(() => {
    emit('update:content', editor.getValue())
  })
}

// 类型切换
const handleTypeChange = (type) => {
  emit('update:type', type)

  if (type === 'json' || type === 'raw') {
    nextTick(() => initEditor())
  } else if (type === 'form' || type === 'form-data') {
    initFormData()
  } else {
    emit('update:content', '')
  }
}

// Form 输入处理
const handleFormInput = (row) => {
  const lastRow = formData.value[formData.value.length - 1]
  if (row === lastRow && (row.key || row.value)) {
    formData.value.push({ key: '', value: '', type: 'text', enabled: true })
  }
  emitFormUpdate()
}

const removeFormRow = (index) => {
  formData.value.splice(index, 1)
  if (formData.value.length === 0) {
    formData.value.push({ key: '', value: '', type: 'text', enabled: true })
  }
  emitFormUpdate()
}

const emitFormUpdate = () => {
  const validData = formData.value.filter(item => item.key || item.value)
  emit('update:content', JSON.stringify(validData))
}

// 监听 props 变化
watch(() => props.type, (val) => {
  bodyType.value = val || 'none'
  if (val === 'json' || val === 'raw') {
    nextTick(() => initEditor())
  } else if (val === 'form' || val === 'form-data') {
    initFormData()
  }
})

watch(() => props.content, (val) => {
  if ((bodyType.value === 'json' || bodyType.value === 'raw') && editor) {
    const currentValue = editor.getValue()
    if (val !== currentValue) {
      editor.setValue(val || '')
    }
  }
})

onMounted(() => {
  if (bodyType.value === 'json' || bodyType.value === 'raw') {
    initEditor()
  } else if (bodyType.value === 'form' || bodyType.value === 'form-data') {
    initFormData()
  }
})

onBeforeUnmount(() => {
  if (editor) {
    editor.dispose()
    editor = null
  }
})
</script>

<style lang="scss" scoped>
.body-editor {
  .body-type-selector {
    margin-bottom: 12px;
  }

  .body-content {
    .body-none {
      padding: 40px 0;
      text-align: center;
    }

    .body-code {
      .monaco-container {
        height: 300px;
        border: 1px solid #dcdfe6;
        border-radius: 4px;
      }
    }

    .body-form {
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
  }
}
</style>
