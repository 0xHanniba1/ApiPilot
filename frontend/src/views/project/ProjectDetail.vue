<template>
  <div class="project-detail">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <el-button text @click="$router.push('/projects')">
          <el-icon><ArrowLeft /></el-icon>
          返回
        </el-button>
        <h2 class="page-title">{{ project?.name || '加载中...' }}</h2>
      </div>
    </div>

    <!-- Tabs -->
    <el-tabs v-model="activeTab" class="project-tabs">
      <!-- 用例管理 Tab -->
      <el-tab-pane label="用例管理" name="cases">
        <el-row :gutter="20" class="content-row">
          <!-- 左侧：模块树 -->
          <el-col :span="6">
            <el-card class="module-card">
              <template #header>
                <div class="card-header">
                  <span>模块</span>
                  <el-button type="primary" link size="small" @click="handleCreateModule(null)">
                    <el-icon><Plus /></el-icon>
                    新建
                  </el-button>
                </div>
              </template>
              <div class="module-tree-container">
                <el-tree
                  ref="treeRef"
                  :data="modules"
                  :props="{ label: 'name', children: 'children' }"
                  node-key="id"
                  default-expand-all
                  highlight-current
                  :expand-on-click-node="false"
                  @node-click="handleModuleClick"
                >
                  <template #default="{ node, data }">
                    <div class="tree-node">
                      <span class="node-label">
                        <el-icon><Folder /></el-icon>
                        {{ node.label }}
                      </span>
                      <el-dropdown
                        trigger="click"
                        @click.stop
                        @command="handleModuleCommand($event, data)"
                      >
                        <el-icon class="node-more"><MoreFilled /></el-icon>
                        <template #dropdown>
                          <el-dropdown-menu>
                            <el-dropdown-item command="addChild">
                              <el-icon><Plus /></el-icon>
                              添加子模块
                            </el-dropdown-item>
                            <el-dropdown-item command="edit">
                              <el-icon><Edit /></el-icon>
                              编辑
                            </el-dropdown-item>
                            <el-dropdown-item command="delete" divided>
                              <el-icon><Delete /></el-icon>
                              删除
                            </el-dropdown-item>
                          </el-dropdown-menu>
                        </template>
                      </el-dropdown>
                    </div>
                  </template>
                </el-tree>
                <el-empty v-if="modules.length === 0" description="暂无模块" :image-size="60" />
              </div>
            </el-card>
          </el-col>

          <!-- 右侧：用例列表 -->
          <el-col :span="18">
            <el-card class="case-card">
              <template #header>
                <div class="card-header">
                  <span>
                    用例列表
                    <el-tag v-if="selectedModule" size="small" type="info" style="margin-left: 8px">
                      {{ selectedModule.name }}
                    </el-tag>
                  </span>
                  <el-button
                    type="primary"
                    size="small"
                    :disabled="!selectedModule"
                    @click="handleCreateCase"
                  >
                    <el-icon><Plus /></el-icon>
                    新建用例
                  </el-button>
                </div>
              </template>
              <el-table :data="cases" v-loading="casesLoading" stripe>
                <el-table-column prop="name" label="用例名称" min-width="200" show-overflow-tooltip />
                <el-table-column prop="method" label="方法" width="90" align="center">
                  <template #default="{ row }">
                    <el-tag :class="['method-tag', row.method]" size="small">
                      {{ row.method }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="path" label="路径" min-width="200" show-overflow-tooltip />
                <el-table-column prop="is_active" label="状态" width="80" align="center">
                  <template #default="{ row }">
                    <el-tag :type="row.is_active ? 'success' : 'info'" size="small">
                      {{ row.is_active ? '启用' : '禁用' }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column label="操作" width="200" fixed="right">
                  <template #default="{ row }">
                    <el-button type="primary" link size="small" @click="handleEditCase(row)">
                      编辑
                    </el-button>
                    <el-button type="success" link size="small" @click="handleExecuteCase(row)">
                      执行
                    </el-button>
                    <el-button type="danger" link size="small" @click="handleDeleteCase(row)">
                      删除
                    </el-button>
                  </template>
                </el-table-column>
              </el-table>
              <div v-if="!selectedModule && cases.length === 0" class="empty-tip">
                <el-empty description="请先选择左侧模块" :image-size="80" />
              </div>
            </el-card>
          </el-col>
        </el-row>
      </el-tab-pane>

      <!-- 环境配置 Tab -->
      <el-tab-pane label="环境配置" name="environments">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>环境列表</span>
              <el-button type="primary" size="small" @click="handleCreateEnv">
                <el-icon><Plus /></el-icon>
                新建环境
              </el-button>
            </div>
          </template>
          <el-table :data="environments" v-loading="envLoading" stripe>
            <el-table-column prop="name" label="环境名称" width="150" />
            <el-table-column prop="base_url" label="基础 URL" min-width="250" show-overflow-tooltip />
            <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
            <el-table-column prop="is_default" label="默认" width="80" align="center">
              <template #default="{ row }">
                <el-tag v-if="row.is_default" type="success" size="small">默认</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="200" fixed="right">
              <template #default="{ row }">
                <el-button type="primary" link size="small" @click="handleEditEnv(row)">
                  编辑
                </el-button>
                <el-button type="info" link size="small" @click="handleEnvVariables(row)">
                  变量
                </el-button>
                <el-button type="danger" link size="small" @click="handleDeleteEnv(row)">
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
          <el-empty v-if="environments.length === 0" description="暂无环境配置" />
        </el-card>
      </el-tab-pane>
    </el-tabs>

    <!-- 模块新建/编辑弹窗 -->
    <el-dialog
      v-model="moduleDialogVisible"
      :title="editingModule ? '编辑模块' : '新建模块'"
      width="450px"
      :close-on-click-modal="false"
    >
      <el-form ref="moduleFormRef" :model="moduleForm" :rules="moduleRules" label-width="80px">
        <el-form-item label="模块名称" prop="name">
          <el-input v-model="moduleForm.name" placeholder="请输入模块名称" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="moduleForm.description" type="textarea" :rows="3" placeholder="请输入描述（选填）" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="moduleDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="moduleSubmitting" @click="handleModuleSubmit">确定</el-button>
      </template>
    </el-dialog>

    <!-- 环境新建/编辑弹窗 -->
    <el-dialog
      v-model="envDialogVisible"
      :title="editingEnv ? '编辑环境' : '新建环境'"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form ref="envFormRef" :model="envForm" :rules="envRules" label-width="80px">
        <el-form-item label="环境名称" prop="name">
          <el-input v-model="envForm.name" placeholder="如：开发环境、测试环境" />
        </el-form-item>
        <el-form-item label="基础 URL" prop="base_url">
          <el-input v-model="envForm.base_url" placeholder="如：https://api.example.com" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="envForm.description" type="textarea" :rows="2" placeholder="请输入描述（选填）" />
        </el-form-item>
        <el-form-item label="设为默认">
          <el-switch v-model="envForm.is_default" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="envDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="envSubmitting" @click="handleEnvSubmit">确定</el-button>
      </template>
    </el-dialog>

    <!-- 环境变量弹窗 -->
    <el-dialog
      v-model="varDialogVisible"
      :title="`环境变量 - ${currentEnv?.name || ''}`"
      width="700px"
    >
      <div class="var-header">
        <el-button type="primary" size="small" @click="handleAddVariable">
          <el-icon><Plus /></el-icon>
          添加变量
        </el-button>
      </div>
      <el-table :data="envVariables" v-loading="varLoading" max-height="400">
        <el-table-column prop="key" label="变量名" width="150">
          <template #default="{ row }">
            <el-input v-if="row.editing" v-model="row.key" size="small" />
            <span v-else>{{ row.key }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="value" label="变量值" min-width="200">
          <template #default="{ row }">
            <el-input v-if="row.editing" v-model="row.value" size="small" />
            <span v-else>{{ row.value }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="说明" min-width="150">
          <template #default="{ row }">
            <el-input v-if="row.editing" v-model="row.description" size="small" placeholder="说明" />
            <span v-else>{{ row.description || '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row, $index }">
            <template v-if="row.editing">
              <el-button type="primary" link size="small" @click="handleSaveVariable(row, $index)">保存</el-button>
              <el-button link size="small" @click="handleCancelVariable(row, $index)">取消</el-button>
            </template>
            <template v-else>
              <el-button type="primary" link size="small" @click="row.editing = true">编辑</el-button>
              <el-button type="danger" link size="small" @click="handleDeleteVariable(row)">删除</el-button>
            </template>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  ArrowLeft,
  Plus,
  Folder,
  MoreFilled,
  Edit,
  Delete,
} from '@element-plus/icons-vue'
import {
  getProject,
  getProjectModules,
  createModule,
  updateModule,
  deleteModule,
  getProjectEnvironments,
  getEnvironment,
  createEnvironment,
  updateEnvironment,
  deleteEnvironment,
  addEnvVariable,
  updateEnvVariable,
  deleteEnvVariable,
} from '@/api/project'
import { getModuleCases, deleteCase } from '@/api/case'
import { executeCase } from '@/api/execution'

const route = useRoute()
const router = useRouter()
const projectId = ref(route.params.id)

// 基础数据
const project = ref(null)
const activeTab = ref('cases')

// 模块相关
const modules = ref([])
const selectedModule = ref(null)
const treeRef = ref(null)

// 用例相关
const cases = ref([])
const casesLoading = ref(false)

// 环境相关
const environments = ref([])
const envLoading = ref(false)

// 模块弹窗
const moduleDialogVisible = ref(false)
const moduleSubmitting = ref(false)
const editingModule = ref(null)
const parentModuleId = ref(null)
const moduleFormRef = ref(null)
const moduleForm = reactive({
  name: '',
  description: '',
})
const moduleRules = {
  name: [{ required: true, message: '请输入模块名称', trigger: 'blur' }],
}

// 环境弹窗
const envDialogVisible = ref(false)
const envSubmitting = ref(false)
const editingEnv = ref(null)
const envFormRef = ref(null)
const envForm = reactive({
  name: '',
  base_url: '',
  description: '',
  is_default: false,
})
const envRules = {
  name: [{ required: true, message: '请输入环境名称', trigger: 'blur' }],
  base_url: [{ required: true, message: '请输入基础 URL', trigger: 'blur' }],
}

// 环境变量弹窗
const varDialogVisible = ref(false)
const varLoading = ref(false)
const currentEnv = ref(null)
const envVariables = ref([])

// ==================== 数据获取 ====================

const fetchProject = async () => {
  try {
    const res = await getProject(projectId.value)
    project.value = res.data
  } catch (error) {
    console.error('获取项目详情失败:', error)
  }
}

const fetchModules = async () => {
  try {
    const res = await getProjectModules(projectId.value)
    modules.value = res.data || []
  } catch (error) {
    console.error('获取模块列表失败:', error)
  }
}

const fetchCases = async (moduleId) => {
  casesLoading.value = true
  try {
    const res = await getModuleCases(moduleId)
    cases.value = res.data.items || []
  } catch (error) {
    console.error('获取用例列表失败:', error)
    cases.value = []
  } finally {
    casesLoading.value = false
  }
}

const fetchEnvironments = async () => {
  envLoading.value = true
  try {
    const res = await getProjectEnvironments(projectId.value)
    environments.value = res.data || []
  } catch (error) {
    console.error('获取环境列表失败:', error)
  } finally {
    envLoading.value = false
  }
}

// ==================== 模块操作 ====================

const handleModuleClick = (data) => {
  selectedModule.value = data
  fetchCases(data.id)
}

const handleCreateModule = (parentId) => {
  editingModule.value = null
  parentModuleId.value = parentId
  moduleForm.name = ''
  moduleForm.description = ''
  moduleDialogVisible.value = true
}

const handleModuleCommand = (command, module) => {
  if (command === 'addChild') {
    handleCreateModule(module.id)
  } else if (command === 'edit') {
    editingModule.value = module
    parentModuleId.value = module.parent_id
    moduleForm.name = module.name
    moduleForm.description = module.description || ''
    moduleDialogVisible.value = true
  } else if (command === 'delete') {
    handleDeleteModule(module)
  }
}

const handleModuleSubmit = async () => {
  try {
    await moduleFormRef.value.validate()
    moduleSubmitting.value = true

    if (editingModule.value) {
      await updateModule(editingModule.value.id, {
        name: moduleForm.name,
        description: moduleForm.description,
      })
      ElMessage.success('更新成功')
    } else {
      await createModule(projectId.value, {
        name: moduleForm.name,
        description: moduleForm.description,
        parent_id: parentModuleId.value,
      })
      ElMessage.success('创建成功')
    }

    moduleDialogVisible.value = false
    fetchModules()
  } catch (error) {
    if (error !== false) {
      console.error('提交失败:', error)
    }
  } finally {
    moduleSubmitting.value = false
  }
}

const handleDeleteModule = async (module) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除模块「${module.name}」吗？模块下的用例也会被删除。`,
      '删除确认',
      { type: 'warning' }
    )
    await deleteModule(module.id)
    ElMessage.success('删除成功')

    if (selectedModule.value?.id === module.id) {
      selectedModule.value = null
      cases.value = []
    }
    fetchModules()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
    }
  }
}

// ==================== 用例操作 ====================

const handleCreateCase = () => {
  if (!selectedModule.value) {
    ElMessage.warning('请先选择模块')
    return
  }
  // 保存项目 ID 用于环境选择
  localStorage.setItem('lastProjectId', projectId.value)
  router.push(`/cases/new/edit?moduleId=${selectedModule.value.id}&projectId=${projectId.value}`)
}

const handleEditCase = (testCase) => {
  localStorage.setItem('lastProjectId', projectId.value)
  router.push(`/cases/${testCase.id}/edit?projectId=${projectId.value}`)
}

const handleExecuteCase = async (testCase) => {
  // 获取默认环境
  const defaultEnv = environments.value.find(e => e.is_default) || environments.value[0]
  if (!defaultEnv) {
    ElMessage.warning('请先配置环境')
    return
  }

  try {
    await ElMessageBox.confirm('确定执行此用例？', '执行确认')
    const res = await executeCase({
      test_case_id: testCase.id,
      environment_id: defaultEnv.id,
    })
    if (res.data.status === 'passed') {
      ElMessage.success('执行成功')
    } else {
      ElMessage.warning(`执行完成，状态: ${res.data.status}`)
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('执行失败:', error)
    }
  }
}

const handleDeleteCase = async (testCase) => {
  try {
    await ElMessageBox.confirm(`确定删除用例「${testCase.name}」吗？`, '删除确认', { type: 'warning' })
    await deleteCase(testCase.id)
    ElMessage.success('删除成功')
    fetchCases(selectedModule.value.id)
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
    }
  }
}

// ==================== 环境操作 ====================

const handleCreateEnv = () => {
  editingEnv.value = null
  envForm.name = ''
  envForm.base_url = ''
  envForm.description = ''
  envForm.is_default = false
  envDialogVisible.value = true
}

const handleEditEnv = (env) => {
  editingEnv.value = env
  envForm.name = env.name
  envForm.base_url = env.base_url
  envForm.description = env.description || ''
  envForm.is_default = env.is_default
  envDialogVisible.value = true
}

const handleEnvSubmit = async () => {
  try {
    await envFormRef.value.validate()
    envSubmitting.value = true

    if (editingEnv.value) {
      await updateEnvironment(editingEnv.value.id, envForm)
      ElMessage.success('更新成功')
    } else {
      await createEnvironment(projectId.value, envForm)
      ElMessage.success('创建成功')
    }

    envDialogVisible.value = false
    fetchEnvironments()
  } catch (error) {
    if (error !== false) {
      console.error('提交失败:', error)
    }
  } finally {
    envSubmitting.value = false
  }
}

const handleDeleteEnv = async (env) => {
  try {
    await ElMessageBox.confirm(`确定删除环境「${env.name}」吗？`, '删除确认', { type: 'warning' })
    await deleteEnvironment(env.id)
    ElMessage.success('删除成功')
    fetchEnvironments()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
    }
  }
}

// ==================== 环境变量操作 ====================

const handleEnvVariables = async (env) => {
  currentEnv.value = env
  varLoading.value = true
  varDialogVisible.value = true

  try {
    const res = await getEnvironment(env.id)
    envVariables.value = (res.data.variables || []).map(v => ({ ...v, editing: false }))
  } catch (error) {
    console.error('获取环境变量失败:', error)
    envVariables.value = []
  } finally {
    varLoading.value = false
  }
}

const handleAddVariable = () => {
  envVariables.value.push({
    key: '',
    value: '',
    description: '',
    editing: true,
    isNew: true,
  })
}

const handleSaveVariable = async (row, index) => {
  if (!row.key) {
    ElMessage.warning('请输入变量名')
    return
  }

  try {
    if (row.isNew) {
      const res = await addEnvVariable(currentEnv.value.id, {
        key: row.key,
        value: row.value,
        description: row.description,
      })
      envVariables.value[index] = { ...res.data, editing: false }
    } else {
      await updateEnvVariable(currentEnv.value.id, row.id, {
        key: row.key,
        value: row.value,
        description: row.description,
      })
      row.editing = false
    }
    ElMessage.success('保存成功')
  } catch (error) {
    console.error('保存失败:', error)
  }
}

const handleCancelVariable = (row, index) => {
  if (row.isNew) {
    envVariables.value.splice(index, 1)
  } else {
    row.editing = false
  }
}

const handleDeleteVariable = async (row) => {
  try {
    await ElMessageBox.confirm('确定删除此变量吗？', '删除确认', { type: 'warning' })
    await deleteEnvVariable(currentEnv.value.id, row.id)
    ElMessage.success('删除成功')
    const index = envVariables.value.findIndex(v => v.id === row.id)
    if (index > -1) {
      envVariables.value.splice(index, 1)
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
    }
  }
}

// Tab 切换时加载数据
watch(activeTab, (tab) => {
  if (tab === 'environments' && environments.value.length === 0) {
    fetchEnvironments()
  }
})

onMounted(() => {
  fetchProject()
  fetchModules()
  fetchEnvironments()
})
</script>

<style lang="scss" scoped>
.project-detail {
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

  .project-tabs {
    :deep(.el-tabs__content) {
      padding: 0;
    }
  }

  .content-row {
    min-height: calc(100vh - 220px);
  }

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .module-card {
    height: calc(100vh - 220px);

    :deep(.el-card__body) {
      padding: 0;
      height: calc(100% - 56px);
      overflow: auto;
    }
  }

  .module-tree-container {
    padding: 10px;
  }

  .tree-node {
    flex: 1;
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-right: 8px;

    .node-label {
      display: flex;
      align-items: center;
      gap: 6px;
    }

    .node-more {
      visibility: hidden;
      color: #909399;
      cursor: pointer;

      &:hover {
        color: #409eff;
      }
    }

    &:hover .node-more {
      visibility: visible;
    }
  }

  .case-card {
    min-height: calc(100vh - 220px);

    .empty-tip {
      padding: 60px 0;
    }
  }

  .var-header {
    margin-bottom: 16px;
  }

  // HTTP method 标签样式
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

    &.PATCH {
      background-color: #fff1f0;
      border-color: #ffa39e;
      color: #ff4d4f;
    }

    &.DELETE {
      background-color: #fff2f0;
      border-color: #ffccc7;
      color: #ff4d4f;
    }
  }
}
</style>
