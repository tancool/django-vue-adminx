import { checkPermission } from '@/api/menu'
import store from '@/store'

/**
 * 检查当前用户是否有指定权限
 * @param {string} permissionCode - 权限编码
 * @returns {Promise<boolean>} 是否有权限
 */
export async function hasPermission(permissionCode) {
  const user = store.state.user
  
  // 超级用户拥有所有权限
  if (user.is_superuser) {
    return true
  }
  
  // 检查本地权限列表
  if (user.permissions && user.permissions.includes(permissionCode)) {
    return true
  }
  
  // 如果本地没有，调用后端接口检查
  try {
    const res = await checkPermission(permissionCode)
    return res.has_permission || false
  } catch (e) {
    console.error('权限检查失败:', e)
    return false
  }
}

/**
 * 同步检查权限（仅检查本地权限列表，不调用后端）
 * @param {string} permissionCode - 权限编码
 * @returns {boolean} 是否有权限
 */
export function hasPermissionSync(permissionCode) {
  const user = store.state.user
  
  // 超级用户拥有所有权限
  if (user.is_superuser) {
    return true
  }
  
  // 检查本地权限列表
  return user.permissions && user.permissions.includes(permissionCode)
}

