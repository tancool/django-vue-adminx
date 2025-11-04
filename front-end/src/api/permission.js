import request from '@/utils/request'

/**
 * 权限 CRUD 接口
 */
export function getPermissionList(params) {
  return request({ 
    url: '/api/rbac/permissions/', 
    method: 'get',
    params
  })
}

export function getPermissionDetail(id) {
  return request({ 
    url: `/api/rbac/permissions/${id}/`, 
    method: 'get'
  })
}

export function createPermission(data) {
  return request({ 
    url: '/api/rbac/permissions/', 
    method: 'post',
    data
  })
}

export function updatePermission(id, data) {
  return request({ 
    url: `/api/rbac/permissions/${id}/`, 
    method: 'put',
    data
  })
}

export function patchPermission(id, data) {
  return request({ 
    url: `/api/rbac/permissions/${id}/`, 
    method: 'patch',
    data
  })
}

export function deletePermission(id) {
  return request({ 
    url: `/api/rbac/permissions/${id}/`, 
    method: 'delete'
  })
}

