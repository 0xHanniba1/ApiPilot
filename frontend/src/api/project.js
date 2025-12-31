import request from './index'

// ==================== 项目 ====================

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

// ==================== 模块 ====================

// 获取项目模块树
export function getProjectModules(projectId) {
  return request.get(`/projects/${projectId}/modules`)
}

// 创建模块
export function createModule(projectId, data) {
  return request.post(`/projects/${projectId}/modules`, data)
}

// 更新模块
export function updateModule(id, data) {
  return request.put(`/modules/${id}`, data)
}

// 删除模块
export function deleteModule(id) {
  return request.delete(`/modules/${id}`)
}

// ==================== 环境 ====================

// 获取项目环境列表
export function getProjectEnvironments(projectId) {
  return request.get(`/projects/${projectId}/environments`)
}

// 获取环境详情（含变量）
export function getEnvironment(id) {
  return request.get(`/environments/${id}`)
}

// 创建环境
export function createEnvironment(projectId, data) {
  return request.post(`/projects/${projectId}/environments`, data)
}

// 更新环境
export function updateEnvironment(id, data) {
  return request.put(`/environments/${id}`, data)
}

// 删除环境
export function deleteEnvironment(id) {
  return request.delete(`/environments/${id}`)
}

// 添加环境变量
export function addEnvVariable(envId, data) {
  return request.post(`/environments/${envId}/variables`, data)
}

// 更新环境变量
export function updateEnvVariable(envId, varId, data) {
  return request.put(`/environments/${envId}/variables/${varId}`, data)
}

// 删除环境变量
export function deleteEnvVariable(envId, varId) {
  return request.delete(`/environments/${envId}/variables/${varId}`)
}

// ==================== 测试集 ====================

// 获取项目测试集列表
export function getProjectSuites(projectId) {
  return request.get(`/projects/${projectId}/suites`)
}
