import request from '@/utils/request'

export function listTasks(params) {
  return request({ url: '/api/tasks/tasks/', method: 'get', params })
}

export function createTask(data) {
  return request({ url: '/api/tasks/tasks/', method: 'post', data })
}

export function updateTask(id, data) {
  return request({ url: `/api/tasks/tasks/${id}/`, method: 'put', data })
}

export function deleteTask(id) {
  return request({ url: `/api/tasks/tasks/${id}/`, method: 'delete' })
}

export function runTaskNow(id) {
  return request({ url: `/api/tasks/tasks/${id}/run_now/`, method: 'post' })
}

