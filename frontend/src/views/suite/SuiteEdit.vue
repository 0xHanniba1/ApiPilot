<template>
  <div class="suite-edit" v-loading="pageLoading">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <el-button text @click="goBack">
          <el-icon><ArrowLeft /></el-icon>
          返回
        </el-button>
        <el-input
          v-model="suiteData.name"
          placeholder="测试集名称"
          class="suite-name-input"
          maxlength="100"
        />
      </div>
      <div class="header-right">
        <el-button type="success" @click="handleExecute">
          <el-icon><VideoPlay /></el-icon>
          执行
        </el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">
          <el-icon><Check /></el-icon>
          保存
        </el-button>
      </div>
    </div>

    <!-- 主内容区 -->
    <el-row :gutter="20" class="main-content">
      <!-- 左侧：已选用例 -->
      <el-col :span="14">
        <el-card class="selected-cases-card">
          <template #header>
            <div class="card-header">
              <span>已选用例 ({{ selectedCases.length }})</span>
              <div class="header-actions">
                <el-radio-group v-model="suiteData.execution_mode" size="small">
                  <el-radio-button value="sequential">顺序</el-radio-button>
                  <el-radio-button value="parallel">并行</el-radio-button>
                </el-radio-group>
              </div>
            </div>
          </template>

          <div v-if="selectedCases.length === 0" class="empty-state">
            <el-empty description="请从右侧选择用例添加" :image-size="80" />
          </div>

          <div v-else class="case-list">
            <div
              v-for="(caseItem, index) in selectedCases"
              :key="caseItem.id"
              class="case-item"
              draggable="true"
              @dragstart="handleDragStart($event, index)"
              @dragover.prevent="handleDragOver($event, index)"
              @drop="handleDrop($event, index)"
              @dragend="handleDragEnd"
              :class="{ 'dragging': dragIndex === index, 'drag-over': dragOverIndex === index }"
            >
              <div class="case-index">
                <el-icon class="drag-handle"><Rank /></el-icon>
                <span>{{ index + 1 }}</span>
              </div>
              <div class="case-info">
                <div class="case-name">{{ caseItem.name }}</div>
                <div class="case-meta">
                  <el-tag :class="['method-tag', caseItem.method]" size="small">
                    {{ caseItem.method }}
                  </el-tag>
                  <span class="case-path">{{ caseItem.path }}</span>
                </div>
              </div>
              <el-button
                type="danger"
                link
                size="small"
                @click="removeCase(index)"
              >
                <el-icon><Delete /></el-icon>
              </el-button>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 右侧：可选用例 -->
      <el-col :span="10">
        <el-card class="available-cases-card">
          <template #header>
            <div class="card-header">
              <span>选择用例</span>
            </div>
          </template>

          <!-- 项目/模块筛选 -->
          <div class="filter-section">
            <el-select
              v-model="filterProjectId"
              placeholder="选择项目"
              clearable
              style="width: 100%; margin-bottom: 10px"
              @change="handleProjectChange"
            >
              <el-option
                v-for="project in projects"
                :key="project.id"
                :label="project.name"
                :value="project.id"
              />
            </el-select>

            <el-tree-select
              v-model="filterModuleId"
              :data="modules"
              :props="{ label: 'name', children: 'children' }"
              placeholder="选择模块"
              clearable
              check-strictly
              style="width: 100%"
              @change="fetchAvailableCases"
            />
          </div>

          <!-- 用例列表 -->
          <div class="available-list" v-loading="casesLoading">
            <div v-if="availableCases.length === 0" class="empty-tip">
              <el-text type="info">请先选择项目和模块</el-text>
            </div>
            <div
              v-for="caseItem in availableCases"
              :key="caseItem.id"
              class="available-item"
              :class="{ 'selected': isCaseSelected(caseItem.id) }"
              @click="toggleCase(caseItem)"
            >
              <el-checkbox :model-value="isCaseSelected(caseItem.id)" />
              <div class="item-info">
                <div class="item-name">{{ caseItem.name }}</div>
                <div class="item-meta">
                  <el-tag :class="['method-tag', caseItem.method]" size="small">
                    {{ caseItem.method }}
                  </el-tag>
                  <span class="item-path">{{ caseItem.path }}</span>
                </div>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 执行弹窗 -->
    <el-dialog v-model="executeDialogVisible" title="执行测试集" width="400px">
      <el-form label-width="80px">
        <el-form-item label="选择环境">
          <el-select v-model="executeEnvId" placeholder="选择执行环境" style="width: 100%">
            <el-option
              v-for="env in environments"
              :key="env.id"
              :label="env.name"
              :value="env.id"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="executeDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="executing" @click="confirmExecute">
          开始执行
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft, Check, VideoPlay, Delete, Rank } from '@element-plus/icons-vue'
import { getSuite, updateSuite, getSuiteCases, addCaseToSuite, removeCaseFromSuite, updateSuiteCasesOrder } from '@/api/suite'
import { executeSuite } from '@/api/execution'
import { getProjects, getProjectModules, getProjectEnvironments } from '@/api/project'
import { getModuleCases } from '@/api/case'

const route = useRoute()
const router = useRouter()

const suiteId = computed(() => route.params.id)

// 页面状态
const pageLoading = ref(false)
const saving = ref(false)
const casesLoading = ref(false)

// 测试集数据
const suiteData = reactive({
  name: '',
  description: '',
  execution_mode: 'sequential',
  project_id: null,
})

// 已选用例
const selectedCases = ref([])

// 可选用例相关
const projects = ref([])
const modules = ref([])
const availableCases = ref([])
const filterProjectId = ref(null)
const filterModuleId = ref(null)

// 执行相关
const executeDialogVisible = ref(false)
const executing = ref(false)
const executeEnvId = ref(null)
const environments = ref([])

// 拖拽相关
const dragIndex = ref(null)
const dragOverIndex = ref(null)

// 判断用例是否已选
const isCaseSelected = (caseId) => {
  return selectedCases.value.some(c => c.id === caseId)
}

// 获取测试集详情
const fetchSuite = async () => {
  pageLoading.value = true
  try {
    const res = await getSuite(suiteId.value)
    const data = res.data
    suiteData.name = data.name
    suiteData.description = data.description
    suiteData.execution_mode = data.execution_mode || 'sequential'
    suiteData.project_id = data.project_id

    // 设置默认筛选项目
    filterProjectId.value = data.project_id
    if (data.project_id) {
      await fetchModules(data.project_id)
      await fetchEnvironments(data.project_id)
    }

    // 获取已选用例
    const casesRes = await getSuiteCases(suiteId.value)
    selectedCases.value = casesRes.data || []
  } catch (error) {
    console.error('获取测试集详情失败:', error)
    ElMessage.error('获取测试集详情失败')
  } finally {
    pageLoading.value = false
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

// 获取模块列表
const fetchModules = async (projectId) => {
  try {
    const res = await getProjectModules(projectId)
    modules.value = res.data || []
  } catch (error) {
    console.error('获取模块列表失败:', error)
  }
}

// 获取环境列表
const fetchEnvironments = async (projectId) => {
  try {
    const res = await getProjectEnvironments(projectId)
    environments.value = res.data || []
    if (environments.value.length > 0) {
      const defaultEnv = environments.value.find(e => e.is_default) || environments.value[0]
      executeEnvId.value = defaultEnv.id
    }
  } catch (error) {
    console.error('获取环境列表失败:', error)
  }
}

// 获取可选用例
const fetchAvailableCases = async () => {
  if (!filterModuleId.value) {
    availableCases.value = []
    return
  }

  casesLoading.value = true
  try {
    const res = await getModuleCases(filterModuleId.value)
    availableCases.value = res.data.items || []
  } catch (error) {
    console.error('获取用例列表失败:', error)
  } finally {
    casesLoading.value = false
  }
}

// 项目切换
const handleProjectChange = async (projectId) => {
  filterModuleId.value = null
  availableCases.value = []
  if (projectId) {
    await fetchModules(projectId)
    await fetchEnvironments(projectId)
  } else {
    modules.value = []
  }
}

// 切换用例选中状态
const toggleCase = (caseItem) => {
  const index = selectedCases.value.findIndex(c => c.id === caseItem.id)
  if (index > -1) {
    selectedCases.value.splice(index, 1)
  } else {
    selectedCases.value.push({ ...caseItem })
  }
}

// 移除用例
const removeCase = (index) => {
  selectedCases.value.splice(index, 1)
}

// 拖拽排序
const handleDragStart = (e, index) => {
  dragIndex.value = index
  e.dataTransfer.effectAllowed = 'move'
}

const handleDragOver = (e, index) => {
  e.dataTransfer.dropEffect = 'move'
  dragOverIndex.value = index
}

const handleDrop = (e, index) => {
  if (dragIndex.value === null || dragIndex.value === index) return

  const dragItem = selectedCases.value[dragIndex.value]
  selectedCases.value.splice(dragIndex.value, 1)
  selectedCases.value.splice(index, 0, dragItem)

  dragIndex.value = null
  dragOverIndex.value = null
}

const handleDragEnd = () => {
  dragIndex.value = null
  dragOverIndex.value = null
}

// 保存
const handleSave = async () => {
  if (!suiteData.name) {
    ElMessage.warning('请输入测试集名称')
    return
  }

  saving.value = true
  try {
    // 更新测试集基本信息
    await updateSuite(suiteId.value, {
      name: suiteData.name,
      description: suiteData.description,
      execution_mode: suiteData.execution_mode,
    })

    // 更新用例顺序
    await updateSuiteCasesOrder(suiteId.value, {
      case_ids: selectedCases.value.map(c => c.id),
    })

    ElMessage.success('保存成功')
  } catch (error) {
    console.error('保存失败:', error)
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

// 执行
const handleExecute = () => {
  if (selectedCases.value.length === 0) {
    ElMessage.warning('请先添加用例')
    return
  }
  executeDialogVisible.value = true
}

const confirmExecute = async () => {
  if (!executeEnvId.value) {
    ElMessage.warning('请选择执行环境')
    return
  }

  executing.value = true
  try {
    const res = await executeSuite({
      suite_id: suiteId.value,
      environment_id: executeEnvId.value,
    })
    ElMessage.success('测试集已开始执行')
    executeDialogVisible.value = false

    if (res.data?.execution_id) {
      router.push(`/executions/${res.data.execution_id}`)
    }
  } catch (error) {
    console.error('执行失败:', error)
    ElMessage.error('执行失败')
  } finally {
    executing.value = false
  }
}

// 返回
const goBack = () => {
  router.back()
}

onMounted(() => {
  fetchProjects()
  fetchSuite()
})
</script>

<style lang="scss" scoped>
.suite-edit {
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

      .suite-name-input {
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
    overflow: hidden;

    .selected-cases-card,
    .available-cases-card {
      height: calc(100vh - 160px);
      display: flex;
      flex-direction: column;

      :deep(.el-card__body) {
        flex: 1;
        overflow: auto;
        padding: 0;
      }

      .card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
      }
    }
  }

  .empty-state {
    height: 300px;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .case-list {
    padding: 12px;

    .case-item {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 12px;
      background: #fff;
      border: 1px solid #ebeef5;
      border-radius: 4px;
      margin-bottom: 8px;
      cursor: move;
      transition: all 0.2s;

      &:hover {
        border-color: #409eff;
      }

      &.dragging {
        opacity: 0.5;
      }

      &.drag-over {
        border-color: #409eff;
        border-style: dashed;
      }

      .case-index {
        display: flex;
        align-items: center;
        gap: 8px;
        min-width: 50px;
        color: #909399;

        .drag-handle {
          cursor: grab;
        }
      }

      .case-info {
        flex: 1;

        .case-name {
          font-weight: 500;
          margin-bottom: 4px;
        }

        .case-meta {
          display: flex;
          align-items: center;
          gap: 8px;

          .case-path {
            color: #909399;
            font-size: 12px;
          }
        }
      }
    }
  }

  .filter-section {
    padding: 12px;
    border-bottom: 1px solid #ebeef5;
  }

  .available-list {
    padding: 12px;

    .empty-tip {
      text-align: center;
      padding: 40px 0;
    }

    .available-item {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 10px 12px;
      border-radius: 4px;
      cursor: pointer;
      transition: background 0.2s;

      &:hover {
        background: #f5f7fa;
      }

      &.selected {
        background: #ecf5ff;
      }

      .item-info {
        flex: 1;

        .item-name {
          font-weight: 500;
          margin-bottom: 4px;
        }

        .item-meta {
          display: flex;
          align-items: center;
          gap: 8px;

          .item-path {
            color: #909399;
            font-size: 12px;
          }
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
