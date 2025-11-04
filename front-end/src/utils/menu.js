import Layout from '@/layout/content'
import { loadComponent } from './component-loader'

/**
 * 将后端菜单树转换为 Vue Router 路由
 * @param {Array} menuTree - 后端返回的菜单树
 * @returns {Array} Vue Router 路由配置
 */
export function menuTreeToRoutes(menuTree) {
  const routes = []

  function processMenu(menu, parentPath = '') {
    // 如果有 children，说明是父菜单
    if (menu.children && menu.children.length > 0) {
      // 处理父菜单路径
      let parentRoutePath = menu.path || `/${menu.id}`
      // 确保路径以 / 开头
      if (!parentRoutePath.startsWith('/')) {
        parentRoutePath = `/${parentRoutePath}`
      }
      
      // 处理子路由
      const children = menu.children
        .map(child => processMenu(child, parentRoutePath))
        .filter(Boolean)
      
      if (children.length === 0) {
        return null
      }
      
      // 创建父路由
      const route = {
        path: parentRoutePath,
        component: Layout,
        meta: {
          title: menu.title,
          icon: menu.icon || 'icon-apps',
        },
        children: children
      }
      
      // 如果父菜单没有 component，将第一个子菜单作为默认路由
      if (children.length > 0 && !menu.component) {
        // 添加重定向到第一个子菜单
        const firstChild = children[0]
        // 构建完整的路径：父路径 + 子路径
        let redirectPath = firstChild.path
        if (!redirectPath.startsWith('/')) {
          // 如果是相对路径，拼接父路径
          redirectPath = `${parentRoutePath}/${redirectPath}`.replace(/\/+/g, '/')
        }
        // 使用命名路由更可靠
        if (firstChild.name) {
          route.redirect = { name: firstChild.name }
        } else {
          route.redirect = redirectPath
        }
      }
      
      return route
    } else {
      // 叶子节点，创建实际页面路由
      let routePath = menu.path || `/${menu.id}`
      
      // 如果是子路由，需要处理为相对路径
      if (parentPath && routePath.startsWith(parentPath)) {
        // 提取相对路径部分
        routePath = routePath.replace(parentPath, '')
        // 如果路径为空，使用父路径
        if (!routePath || routePath === '/') {
          routePath = parentPath
        }
        // 确保相对路径不以 / 开头（Vue Router 子路由规范）
        if (routePath.startsWith('/')) {
          routePath = routePath.substring(1)
        }
        // 如果提取后为空，使用默认名称
        if (!routePath) {
          routePath = `menu_${menu.id}`
        }
      } else {
        // 顶层路由，确保以 / 开头
        if (!routePath.startsWith('/')) {
          routePath = `/${routePath}`
        }
      }
      
      // 生成路由名称
      const routeName = menu.path?.replace(/\//g, '_').replace(/^_/, '') || `menu_${menu.id}`
      
      return {
        path: routePath,
        name: routeName,
        component: () => {
          // 根据 component 路径动态加载组件
          if (menu.component) {
            // 使用组件加载器加载组件
            return loadComponent(menu.component)
          }
          // 如果没有 component，使用默认菜单页面
          return import('@/views/menu-page/index.vue')
        },
        meta: {
          title: menu.title,
          icon: menu.icon,
          menuId: menu.id, // 保存菜单ID，方便默认页面查找菜单信息
        }
      }
    }
  }

  menuTree.forEach(menu => {
    const route = processMenu(menu)
    if (route) {
      routes.push(route)
    }
  })

  return routes
}

/**
 * 扁平化菜单树（用于侧边栏展示）
 * @param {Array} menuTree - 菜单树
 * @returns {Array} 扁平化的菜单列表
 */
export function flattenMenuTree(menuTree) {
  const result = []

  function traverse(menu, parentPath = '') {
    const menuItem = {
      ...menu,
      fullPath: parentPath ? `${parentPath}${menu.path}` : menu.path
    }
    
    if (menu.children && menu.children.length > 0) {
      result.push(menuItem)
      menu.children.forEach(child => traverse(child, menuItem.fullPath))
    } else {
      result.push(menuItem)
    }
  }

  menuTree.forEach(menu => traverse(menu))
  return result
}

