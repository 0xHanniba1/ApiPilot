import request from './index'

// 获取测试集列表
export function getSuites(params) {
  return request.get('/suites', { params })
}

// 获取测试集详情
export function getSuite(id) {
  return request.get(`/suites/${id}`)
}

// 创建测试集
export function createSuite(data) {
  return request.post('/suites', data)
}

// 更新测试集
export function updateSuite(id, data) {
  return request.put(`/suites/${id}`, data)
}

// 删除测试集
export function deleteSuite(id) {
  return request.delete(`/suites/${id}`)
}

// 获取测试集用例列表
export function getSuiteCases(suiteId) {
  return request.get(`/suites/${suiteId}/cases`)
}

// 添加用例到测试集
export function addCaseToSuite(suiteId, data) {
  return request.post(`/suites/${suiteId}/cases`, data)
}

// 从测试集移除用例
export function removeCaseFromSuite(suiteId, caseId) {
  return request.delete(`/suites/${suiteId}/cases/${caseId}`)
}

// 更新测试集用例顺序
export function updateSuiteCasesOrder(suiteId, data) {
  return request.put(`/suites/${suiteId}/cases/order`, data)
}

// 执行测试集
export function executeSuite(suiteId, data) {
  return request.post(`/suites/${suiteId}/execute`, data)
}
