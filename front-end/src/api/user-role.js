import request from '@/utils/request'

/**
 * 用户角色 CRUD 接口
 */
export function getUserRoleList(params) {
  return request({ 
    url: '/api/rbac/user-roles/', 
    method: 'get',
    params
  })
}

export function getUserRoleDetail(id) {
  return request({ 
    url: `/api/rbac/user-roles/${id}/`, 
    method: 'get'
  })
}

export function createUserRole(data) {
  return request({ 
    url: '/api/rbac/user-roles/', 
    method: 'post',
    data
  })
}

export function updateUserRole(id, data) {
  return request({ 
    url: `/api/rbac/user-roles/${id}/`, 
    method: 'put',
    data
  })
}

export function patchUserRole(id, data) {
  return request({ 
    url: `/api/rbac/user-roles/${id}/`, 
    method: 'patch',
    data
  })
}

export function deleteUserRole(id) {
  return request({ 
    url: `/api/rbac/user-roles/${id}/`, 
    method: 'delete'
  })
}

