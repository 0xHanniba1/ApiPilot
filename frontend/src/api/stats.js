import request from './index'

// 获取首页统计数据
export function getDashboardStats() {
  return request.get('/stats/dashboard')
}

// 获取项目执行趋势
export function getProjectTrend(projectId, days = 7) {
  return request.get(`/stats/projects/${projectId}/trend`, { params: { days } })
}

// 获取失败率最高的用例
export function getTopFailures(params) {
  return request.get('/stats/cases/top-failures', { params })
}

// 获取测试集执行历史
export function getSuiteHistory(suiteId, limit = 20) {
  return request.get(`/stats/suites/${suiteId}/history`, { params: { limit } })
}
