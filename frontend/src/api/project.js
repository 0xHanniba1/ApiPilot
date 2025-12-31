import request from './index'

// 获取项目列表
export function getProjects(params) {
  return request.get('/projects', { params })
}

// 获取项目详情
export function getProject(id) {
  return request.get(`/projects/${id}`)
}

// 创建项目
export function createProject(data) {
  return request.post('/projects', data)
}

// 更新项目
export function updateProject(id, data) {
  return request.put(`/projects/${id}`, data)
}

// 删除项目
export function deleteProject(id) {
  return request.delete(`/projects/${id}`)
}

// 获取项目模块树
export function getProjectModules(projectId) {
  return request.get(`/projects/${projectId}/modules`)
}

// 获取项目环境列表
export function getProjectEnvironments(projectId) {
  return request.get(`/projects/${projectId}/environments`)
}

// 获取项目测试集列表
export function getProjectSuites(projectId) {
  return request.get(`/projects/${projectId}/suites`)
}
