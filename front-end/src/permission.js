import router, { addDynamicRoutes } from '@/router'
import store from '@/store'
import { Message } from '@arco-design/web-vue'

// 标记是否已加载菜单
let menuLoaded = false

router.beforeEach(async (to, from, next) => {
  // 登录页直接放行
  if (to.path === '/login') {
    menuLoaded = false // 退出登录时重置
    next()
    return
  }

  // 检查是否有用户信息
  const hasUserInfo = store.state.user.id
  
  if (!hasUserInfo) {
    // 尝试获取用户信息（验证 Session 是否有效）
    try {
      const success = await store.dispatch('user/getUserInfo')
      if (!success) {
        Message.info('请先登录')
        next('/login')
        return
      }
    } catch (e) {
    Message.info('请先登录')
    next('/login')
    return
    }
  }

  // 如果还没加载菜单，则加载菜单并添加路由
  if (!menuLoaded) {
    try {
      const success = await store.dispatch('menu/getMenuTree')
      if (success) {
        const menuTree = store.state.menu.menuTree
        if (menuTree && menuTree.length > 0) {
          addDynamicRoutes(menuTree)
          menuLoaded = true
          
          // 路由添加完成后，重新匹配当前路径
          // 如果当前路由是根路径或找不到匹配的路由，重定向到第一个菜单
          if (to.path === '/' || to.path === '' || to.matched.length === 0) {
            const firstMenu = findFirstMenu(menuTree)
            if (firstMenu && firstMenu.path) {
              // 确保路径以 / 开头
              const firstPath = firstMenu.path.startsWith('/') 
                ? firstMenu.path 
                : `/${firstMenu.path}`
              next(firstPath)
              return
            }
          }
        }
      }
    } catch (e) {
      console.error('加载菜单失败:', e)
    }
  }

  // 如果路由匹配失败（404），且不是登录页，尝试重定向到第一个菜单
  if (to.matched.length === 0 && to.path !== '/login' && menuLoaded) {
    const menuTree = store.state.menu.menuTree
    if (menuTree && menuTree.length > 0) {
      const firstMenu = findFirstMenu(menuTree)
      if (firstMenu && firstMenu.path) {
        const firstPath = firstMenu.path.startsWith('/') 
          ? firstMenu.path 
          : `/${firstMenu.path}`
        next(firstPath)
        return
      }
    }
  }

  next()
})

/**
 * 查找第一个可访问的菜单路径
 */
function findFirstMenu(menuTree) {
  for (const menu of menuTree) {
    if (menu.children && menu.children.length > 0) {
      const firstChild = findFirstMenu(menu.children)
      if (firstChild) return firstChild
    } else if (menu.path) {
      return menu
    }
  }
  return null
}
