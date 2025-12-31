<template>
  <div class="project-list">
    <div class="page-header">
      <h2 class="page-title">项目管理</h2>
      <el-button type="primary" @click="handleCreate">
        <el-icon><Plus /></el-icon>
        新建项目
      </el-button>
    </div>

    <!-- 搜索栏 -->
    <div class="search-bar">
      <el-input
        v-model="searchKeyword"
        placeholder="搜索项目名称"
        prefix-icon="Search"
        clearable
        style="width: 300px"
        @input="handleSearch"
      />
    </div>

    <!-- 项目卡片 -->
    <div v-loading="loading" class="project-cards">
      <el-row :gutter="20">
        <el-col
          v-for="project in filteredProjects"
          :key="project.id"
          :xs="24"
          :sm="12"
          :md="8"
          :lg="6"
        >
          <el-card class="project-card" shadow="hover" @click="goToDetail(project.id)">
            <template #header>
              <div class="card-header">
                <div class="project-name">
                  <el-icon class="project-icon"><Folder /></el-icon>
                  <span>{{ project.name }}</span>
                </div>
                <el-dropdown trigger="click" @click.stop @command="handleCommand($event, project)">
                  <el-icon class="more-btn"><MoreFilled /></el-icon>
                  <template #dropdown>
                    <el-dropdown-menu>
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
            <div class="card-body">
              <p class="project-desc">{{ project.description || '暂无描述' }}</p>
              <div class="project-meta">
                <span class="meta-item">
                  <el-icon><Clock /></el-icon>
                  {{ formatDate(project.created_at) }}
                </span>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 空状态 -->
      <el-empty v-if="!loading && filteredProjects.length === 0" description="暂无项目">
        <el-button type="primary" @click="handleCreate">创建第一个项目</el-button>
      </el-empty>
    </div>

    <!-- 分页 -->
    <div v-if="total > pageSize" class="pagination">
      <el-pagination
        :current-page="page"
        :page-size="pageSize"
        :total="total"
        layout="total, prev, pager, next"
        @current-change="handlePageChange"
      />
    </div>

    <!-- 新建/编辑弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      :title="editingProject ? '编辑项目' : '新建项目'"
      width="500px"
      :close-on-click-modal="false"
      @closed="resetForm"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="80px"
        label-position="left"
      >
        <el-form-item label="项目名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入项目名称" maxlength="100" show-word-limit />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="4"
            placeholder="请输入项目描述（选填）"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus,
  Folder,
  MoreFilled,
  Edit,
  Delete,
  Clock,
  Search,
} from '@element-plus/icons-vue'
import { getProjects, createProject, updateProject, deleteProject } from '@/api/project'

const router = useRouter()

// 数据状态
const projects = ref([])
const loading = ref(false)
const page = ref(1)
const pageSize = ref(12)
const total = ref(0)
const searchKeyword = ref('')

// 弹窗状态
const dialogVisible = ref(false)
const submitting = ref(false)
const editingProject = ref(null)
const formRef = ref(null)

const form = reactive({
  name: '',
  description: '',
})

const rules = {
  name: [
    { required: true, message: '请输入项目名称', trigger: 'blur' },
    { min: 2, max: 100, message: '项目名称长度为 2-100 个字符', trigger: 'blur' },
  ],
}

// 过滤项目
const filteredProjects = computed(() => {
  if (!searchKeyword.value) return projects.value
  const keyword = searchKeyword.value.toLowerCase()
  return projects.value.filter(p =>
    p.name.toLowerCase().includes(keyword) ||
    (p.description && p.description.toLowerCase().includes(keyword))
  )
})

// 格式化日期
const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN')
}

// 获取项目列表
const fetchProjects = async () => {
  loading.value = true
  try {
    const res = await getProjects({ page: page.value, page_size: pageSize.value })
    projects.value = res.data.items || []
    total.value = res.data.total || 0
  } catch (error) {
    console.error('获取项目列表失败:', error)
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  // 前端过滤，无需请求
}

// 分页
const handlePageChange = (newPage) => {
  page.value = newPage
  fetchProjects()
}

// 跳转详情
const goToDetail = (id) => {
  router.push(`/projects/${id}`)
}

// 新建项目
const handleCreate = () => {
  editingProject.value = null
  dialogVisible.value = true
}

// 下拉菜单命令
const handleCommand = (command, project) => {
  if (command === 'edit') {
    handleEdit(project)
  } else if (command === 'delete') {
    handleDelete(project)
  }
}

// 编辑项目
const handleEdit = (project) => {
  editingProject.value = project
  form.name = project.name
  form.description = project.description || ''
  dialogVisible.value = true
}

// 删除项目
const handleDelete = async (project) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除项目「${project.name}」吗？删除后无法恢复。`,
      '删除确认',
      {
        type: 'warning',
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
      }
    )
    await deleteProject(project.id)
    ElMessage.success('删除成功')
    fetchProjects()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
    }
  }
}

// 提交表单
const handleSubmit = async () => {
  try {
    await formRef.value.validate()
    submitting.value = true

    if (editingProject.value) {
      await updateProject(editingProject.value.id, {
        name: form.name,
        description: form.description,
      })
      ElMessage.success('更新成功')
    } else {
      await createProject({
        name: form.name,
        description: form.description,
      })
      ElMessage.success('创建成功')
    }

    dialogVisible.value = false
    fetchProjects()
  } catch (error) {
    if (error !== false) {
      console.error('提交失败:', error)
    }
  } finally {
    submitting.value = false
  }
}

// 重置表单
const resetForm = () => {
  form.name = ''
  form.description = ''
  editingProject.value = null
  formRef.value?.resetFields()
}

onMounted(() => {
  fetchProjects()
})
</script>

<style lang="scss" scoped>
.project-list {
  padding: 20px;

  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;

    .page-title {
      font-size: 20px;
      font-weight: 600;
      color: #303133;
    }
  }

  .search-bar {
    margin-bottom: 20px;
  }

  .project-cards {
    min-height: 400px;
  }

  .project-card {
    margin-bottom: 20px;
    cursor: pointer;
    transition: transform 0.2s, box-shadow 0.2s;

    &:hover {
      transform: translateY(-4px);
    }

    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;

      .project-name {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 16px;
        font-weight: 500;
        color: #303133;

        .project-icon {
          color: #409eff;
          font-size: 20px;
        }
      }

      .more-btn {
        font-size: 16px;
        color: #909399;
        cursor: pointer;
        padding: 4px;
        border-radius: 4px;

        &:hover {
          background-color: #f5f7fa;
          color: #409eff;
        }
      }
    }

    .card-body {
      .project-desc {
        color: #606266;
        font-size: 14px;
        line-height: 1.6;
        margin-bottom: 16px;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
        min-height: 44px;
      }

      .project-meta {
        display: flex;
        gap: 16px;
        color: #909399;
        font-size: 12px;

        .meta-item {
          display: flex;
          align-items: center;
          gap: 4px;
        }
      }
    }
  }

  .pagination {
    margin-top: 20px;
    display: flex;
    justify-content: flex-end;
  }
}
</style>
