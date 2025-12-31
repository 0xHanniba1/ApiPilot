import request from './index'

// 获取模块下的用例列表
export function getModuleCases(moduleId, params) {
  return request.get(`/modules/${moduleId}/cases`, { params })
}

// 获取用例详情
export function getCase(id) {
  return request.get(`/cases/${id}`)
}

// 创建用例
export function createCase(moduleId, data) {
  return request.post(`/modules/${moduleId}/cases`, data)
}

// 更新用例
export function updateCase(id, data) {
  return request.put(`/cases/${id}`, data)
}

// 删除用例
export function deleteCase(id) {
  return request.delete(`/cases/${id}`)
}

// 复制用例
export function copyCase(id) {
  return request.post(`/cases/${id}/copy`)
}
