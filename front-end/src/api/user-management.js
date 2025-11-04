import request from '@/utils/request'

/**
 * 用户管理 CRUD 接口
 */
export function getUserList(params) {
  return request({ 
    url: '/api/rbac/users/', 
    method: 'get',
    params
  })
}

export function getUserDetail(id) {
  return request({ 
    url: `/api/rbac/users/${id}/`, 
    method: 'get'
  })
}

export function createUser(data) {
  return request({ 
    url: '/api/rbac/users/', 
    method: 'post',
    data
  })
}

export function updateUser(id, data) {
  return request({ 
    url: `/api/rbac/users/${id}/`, 
    method: 'put',
    data
  })
}

export function patchUser(id, data) {
  return request({ 
    url: `/api/rbac/users/${id}/`, 
    method: 'patch',
    data
  })
}

export function deleteUser(id) {
  return request({ 
    url: `/api/rbac/users/${id}/`, 
    method: 'delete'
  })
}

