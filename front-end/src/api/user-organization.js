import request from '@/utils/request'

/**
 * 用户组织 CRUD 接口
 */
export function getUserOrganizationList(params) {
  return request({ 
    url: '/api/rbac/user-organizations/', 
    method: 'get',
    params
  })
}

export function getUserOrganizationDetail(id) {
  return request({ 
    url: `/api/rbac/user-organizations/${id}/`, 
    method: 'get'
  })
}

export function createUserOrganization(data) {
  return request({ 
    url: '/api/rbac/user-organizations/', 
    method: 'post',
    data
  })
}

export function updateUserOrganization(id, data) {
  return request({ 
    url: `/api/rbac/user-organizations/${id}/`, 
    method: 'put',
    data
  })
}

export function patchUserOrganization(id, data) {
  return request({ 
    url: `/api/rbac/user-organizations/${id}/`, 
    method: 'patch',
    data
  })
}

export function deleteUserOrganization(id) {
  return request({ 
    url: `/api/rbac/user-organizations/${id}/`, 
    method: 'delete'
  })
}

