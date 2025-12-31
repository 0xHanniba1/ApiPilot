import request from './index'

// 执行单个用例
export function executeCase(data) {
  return request.post('/execute/case', data)
}

// 调试执行（不保存记录）
export function debugExecute(data) {
  return request.post('/execute/debug', data)
}

// 执行测试集
export function executeSuite(data) {
  return request.post('/execute/suite', data)
}

// 获取执行记录列表
export function getExecutions(params) {
  return request.get('/execute/executions', { params })
}

// 获取执行概览
export function getExecution(id) {
  return request.get(`/execute/executions/${id}`)
}

// 获取执行详情
export function getExecutionDetails(id) {
  return request.get(`/execute/executions/${id}/details`)
}
