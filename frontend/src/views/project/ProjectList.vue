<template>
  <div class="page-container">
    <div class="page-header">
      <h2 class="page-title">项目管理</h2>
      <el-button type="primary" @click="showCreateDialog = true">
        <el-icon><Plus /></el-icon>
        新建项目
      </el-button>
    </div>

    <el-table :data="projects" v-loading="loading" stripe>
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="name" label="项目名称" min-width="200">
        <template #default="{ row }">
          <router-link :to="`/projects/${row.id}`" class="project-link">
            {{ row.name }}
          </router-link>
        </template>
      </el-table-column>
      <el-table-column prop="description" label="描述" min-width="300" show-overflow-tooltip />
      <el-table-column prop="created_at" label="创建时间" width="180">
        <template #default="{ row }">
          {{ formatDate(row.created_at) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button type="primary" link @click="$router.push(`/projects/${row.id}`)">
            查看
          </el-button>
          <el-button type="primary" link @click="handleEdit(row)">
            编辑
          </el-button>
          <el-popconfirm title="确定删除该项目？" @confirm="handleDelete(row.id)">
            <template #reference>
              <el-button type="danger" link>删除</el-button>
            </template>
          </el-popconfirm>
        </template>
      </el-table-column>
    </el-table>

    <el-pagination
      v-if="total > 0"
      class="pagination"
      :current-page="page"
      :page-size="pageSize"
      :total="total"
      layout="total, prev, pager, next"
      @current-change="handlePageChange"
    />

    <!-- 新建/编辑对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      :title="editingProject ? '编辑项目' : '新建项目'"
      width="500px"
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
        <el-form-item label="项目名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入项目名称" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="3"
            placeholder="请输入项目描述"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { getProjects, createProject, updateProject, deleteProject } from '@/api/project'

const projects = ref([])
const loading = ref(false)
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)

const showCreateDialog = ref(false)
const submitting = ref(false)
const editingProject = ref(null)
const formRef = ref(null)

const form = reactive({
  name: '',
  description: '',
})

const rules = {
  name: [{ required: true, message: '请输入项目名称', trigger: 'blur' }],
}

// 格式化日期
const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}

// 获取项目列表
const fetchProjects = async () => {
  loading.value = true
  try {
    const res = await getProjects({ page: page.value, page_size: pageSize.value })
    projects.value = res.data.items
    total.value = res.data.total
  } catch (error) {
    console.error('获取项目列表失败:', error)
  } finally {
    loading.value = false
  }
}

// 编辑项目
const handleEdit = (project) => {
  editingProject.value = project
  form.name = project.name
  form.description = project.description || ''
  showCreateDialog.value = true
}

// 提交表单
const handleSubmit = async () => {
  try {
    await formRef.value.validate()
    submitting.value = true

    if (editingProject.value) {
      await updateProject(editingProject.value.id, form)
      ElMessage.success('更新成功')
    } else {
      await createProject(form)
      ElMessage.success('创建成功')
    }

    showCreateDialog.value = false
    resetForm()
    fetchProjects()
  } catch (error) {
    if (error !== false) {
      console.error('提交失败:', error)
    }
  } finally {
    submitting.value = false
  }
}

// 删除项目
const handleDelete = async (id) => {
  try {
    await deleteProject(id)
    ElMessage.success('删除成功')
    fetchProjects()
  } catch (error) {
    console.error('删除失败:', error)
  }
}

// 重置表单
const resetForm = () => {
  editingProject.value = null
  form.name = ''
  form.description = ''
}

// 分页变化
const handlePageChange = (newPage) => {
  page.value = newPage
  fetchProjects()
}

onMounted(() => {
  fetchProjects()
})
</script>

<style lang="scss" scoped>
.project-link {
  color: #409eff;
  text-decoration: none;

  &:hover {
    text-decoration: underline;
  }
}

.pagination {
  margin-top: 20px;
  justify-content: flex-end;
}
</style>
