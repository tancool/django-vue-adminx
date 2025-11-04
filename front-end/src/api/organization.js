import request from '@/utils/request'

/**
 * 组织 CRUD 接口
 */
export function getOrganizationList(params) {
  return request({ 
    url: '/api/rbac/organizations/', 
    method: 'get',
    params
  })
}

export function getOrganizationDetail(id) {
  return request({ 
    url: `/api/rbac/organizations/${id}/`, 
    method: 'get'
  })
}

export function createOrganization(data) {
  return request({ 
    url: '/api/rbac/organizations/', 
    method: 'post',
    data
  })
}

export function updateOrganization(id, data) {
  return request({ 
    url: `/api/rbac/organizations/${id}/`, 
    method: 'put',
    data
  })
}

export function patchOrganization(id, data) {
  return request({ 
    url: `/api/rbac/organizations/${id}/`, 
    method: 'patch',
    data
  })
}

export function deleteOrganization(id) {
  return request({ 
    url: `/api/rbac/organizations/${id}/`, 
    method: 'delete'
  })
}

/**
 * 获取组织树
 * @param {Object} params - { only_active: true/false }
 * @returns {Promise} 返回组织树
 */
export function getOrganizationTree(params) {
  return request({ 
    url: '/api/rbac/organizations/tree/', 
    method: 'get',
    params
  })
}

