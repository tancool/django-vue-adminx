/**
 * 组件加载器：用于动态加载页面组件
 * 解决 Vite 动态 import 路径解析问题
 */

// 使用 Vite 的 import.meta.glob 自动收集所有视图组件
// 相对路径基于当前文件（src/utils），因此使用 ../views
const viewModules = import.meta.glob('../views/**/*.vue')

/**
 * 动态加载组件
 * @param {string} componentPath - 组件路径，如 'system/user/index'
 * @returns {Promise} 组件导入 Promise
 */
export function loadComponent(componentPath) {
  // 规范化：后端给的通常是例如 'system/book/index'
  // 我们按 '../views/${componentPath}.vue' 进行匹配
  const guess = `../views/${componentPath}.vue`
  const loader = viewModules[guess]
  if (loader) return loader()

  // 兼容：若后端未带 index，尝试补全
  const guessIndex = `../views/${componentPath}/index.vue`
  const loaderIndex = viewModules[guessIndex]
  if (loaderIndex) return loaderIndex()

  console.error('加载组件失败: 未找到匹配视图', componentPath)
  return import('@/views/menu-page/index.vue')
}

