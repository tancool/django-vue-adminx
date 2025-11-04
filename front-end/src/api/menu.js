import request from '@/utils/request'

/**
 * 获取菜单树接口
 * @returns {Promise} 返回菜单树数组
 */
export function getMenuTree() {
  return request({ 
    url: '/api/rbac/menu-tree/', 
    method: 'get' 
  })
}

/**
 * 权限检查接口
 * @param {string} code - 权限编码
 * @returns {Promise} 返回 { has_permission: true/false }
 */
export function checkPermission(code) {
  return request({ 
    url: '/api/rbac/auth/check-permission/', 
    method: 'post',
    data: { code }
  })
}

/**
 * 菜单 CRUD 接口
 */
export function getMenuList(params) {
  return request({ 
    url: '/api/rbac/menus/', 
    method: 'get',
    params
  })
}

export function getMenuDetail(id) {
  return request({ 
    url: `/api/rbac/menus/${id}/`, 
    method: 'get'
  })
}

export function createMenu(data) {
  return request({ 
    url: '/api/rbac/menus/', 
    method: 'post',
    data
  })
}

export function updateMenu(id, data) {
  return request({ 
    url: `/api/rbac/menus/${id}/`, 
    method: 'put',
    data
  })
}

export function patchMenu(id, data) {
  return request({ 
    url: `/api/rbac/menus/${id}/`, 
    method: 'patch',
    data
  })
}

export function deleteMenu(id) {
  return request({ 
    url: `/api/rbac/menus/${id}/`, 
    method: 'delete'
  })
}

