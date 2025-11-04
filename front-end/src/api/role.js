import request from '@/utils/request'

/**
 * 角色 CRUD 接口
 */
export function getRoleList(params) {
  return request({ 
    url: '/api/rbac/roles/', 
    method: 'get',
    params
  })
}

export function getRoleDetail(id) {
  return request({ 
    url: `/api/rbac/roles/${id}/`, 
    method: 'get'
  })
}

export function createRole(data) {
  return request({ 
    url: '/api/rbac/roles/', 
    method: 'post',
    data
  })
}

export function updateRole(id, data) {
  return request({ 
    url: `/api/rbac/roles/${id}/`, 
    method: 'put',
    data
  })
}

export function patchRole(id, data) {
  return request({ 
    url: `/api/rbac/roles/${id}/`, 
    method: 'patch',
    data
  })
}

export function deleteRole(id) {
  return request({ 
    url: `/api/rbac/roles/${id}/`, 
    method: 'delete'
  })
}

