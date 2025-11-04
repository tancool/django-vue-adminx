<template>
  <div class="menu-page">
    <a-empty v-if="!menuInfo" description="页面开发中..." />
    <div v-else>
      <a-typography-title :heading="4">{{ menuInfo.title }}</a-typography-title>
      <a-typography-paragraph>
        页面路径: {{ menuInfo.path }}
      </a-typography-paragraph>
      <a-typography-paragraph v-if="menuInfo.component">
        组件路径: {{ menuInfo.component }}
      </a-typography-paragraph>
      <a-alert type="info" style="margin-top: 20px">
        该页面组件尚未创建，请在 <code>src/views/{{ menuInfo.component }}</code> 创建对应组件
      </a-alert>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useStore } from 'vuex'

const route = useRoute()
const store = useStore()

// 根据当前路由查找对应的菜单信息
const menuInfo = computed(() => {
  const menuTree = store.state.menu.menuTree || []
  const currentPath = route.path
  
  function findMenu(menus, path) {
    for (const menu of menus) {
      if (menu.path === path) {
        return menu
      }
      if (menu.children && menu.children.length > 0) {
        const found = findMenu(menu.children, path)
        if (found) return found
      }
    }
    return null
  }
  
  return findMenu(menuTree, currentPath)
})
</script>

<style scoped>
.menu-page {
  padding: 20px;
}
</style>

