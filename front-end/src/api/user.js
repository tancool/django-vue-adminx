import request from '@/utils/request'

/**
 * 登录接口
 * @param {Object} data - 登录数据 { username, password }
 * @returns {Promise} 返回用户信息 { id, username, roles, permissions }
 */
export function login(data) {
  return request({ 
    url: '/api/rbac/auth/login/', 
    method: 'post', 
    data 
  })
}

/**
 * 退出登录接口
 * @returns {Promise}
 */
export function logout() {
  return request({ 
    url: '/api/rbac/auth/logout/', 
    method: 'post' 
  })
}

/**
 * 获取当前用户信息
 * @returns {Promise} 返回用户信息
 */
export function getUserInfo() {
  return request({ 
    url: '/api/rbac/auth/user-info/', 
    method: 'get' 
  })
}

/**
 * 修改密码
 * @param {Object} data - { old_password, new_password }
 * @returns {Promise}
 */
export function changePassword(data) {
  return request({ 
    url: '/api/rbac/auth/change-password/', 
    method: 'post',
    data
  })
}

/**
 * 获取当前用户权限列表
 * @returns {Promise} 返回权限列表
 */
export function getUserPermissions() {
  return request({ 
    url: '/api/rbac/auth/permissions/', 
    method: 'get' 
  })
}

/**
 * 获取当前用户组织信息
 * @returns {Promise} 返回组织信息
 */
export function getUserOrganizations() {
  return request({ 
    url: '/api/rbac/auth/organizations/', 
    method: 'get' 
  })
}
