import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { getProjects, getProject, getProjectModules, getProjectEnvironments } from '@/api/project'

export const useProjectStore = defineStore('project', () => {
  // 状态
  const projects = ref([])
  const currentProject = ref(null)
  const modules = ref([])
  const environments = ref([])
  const loading = ref(false)

  // 计算属性
  const projectCount = computed(() => projects.value.length)

  // 获取项目列表
  async function fetchProjects(params = {}) {
    loading.value = true
    try {
      const res = await getProjects(params)
      projects.value = res.data.items || []
      return res.data
    } finally {
      loading.value = false
    }
  }

  // 获取项目详情
  async function fetchProject(id) {
    loading.value = true
    try {
      const res = await getProject(id)
      currentProject.value = res.data
      return res.data
    } finally {
      loading.value = false
    }
  }

  // 获取模块树
  async function fetchModules(projectId) {
    try {
      const res = await getProjectModules(projectId)
      modules.value = res.data || []
      return res.data
    } catch (error) {
      modules.value = []
      throw error
    }
  }

  // 获取环境列表
  async function fetchEnvironments(projectId) {
    try {
      const res = await getProjectEnvironments(projectId)
      environments.value = res.data || []
      return res.data
    } catch (error) {
      environments.value = []
      throw error
    }
  }

  // 重置状态
  function reset() {
    currentProject.value = null
    modules.value = []
    environments.value = []
  }

  return {
    projects,
    currentProject,
    modules,
    environments,
    loading,
    projectCount,
    fetchProjects,
    fetchProject,
    fetchModules,
    fetchEnvironments,
    reset,
  }
})
