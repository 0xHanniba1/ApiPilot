import request from './index'

// 获取定时任务列表
export function getSchedules(params) {
  return request.get('/schedules', { params })
}

// 获取定时任务详情
export function getSchedule(id) {
  return request.get(`/schedules/${id}`)
}

// 创建定时任务
export function createSchedule(data) {
  return request.post('/schedules', data)
}

// 更新定时任务
export function updateSchedule(id, data) {
  return request.put(`/schedules/${id}`, data)
}

// 删除定时任务
export function deleteSchedule(id) {
  return request.delete(`/schedules/${id}`)
}

// 启用/禁用定时任务
export function toggleSchedule(id, isActive) {
  return request.patch(`/schedules/${id}/toggle`, { is_active: isActive })
}

// 立即执行定时任务
export function runScheduleNow(id) {
  return request.post(`/schedules/${id}/run`)
}

// 获取任务执行历史
export function getScheduleHistory(id, params) {
  return request.get(`/schedules/${id}/history`, { params })
}
