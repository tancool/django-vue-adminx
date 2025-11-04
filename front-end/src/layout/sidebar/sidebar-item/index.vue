<template>
  <!-- 叶子节点（没有子菜单或只有一个子菜单） -->
  <a-menu-item 
    v-if="!item.children || item.children.length === 0" 
    :key="routeName"
    :data-route-name="routeName"
    :data-full-path="fullPath"
  >
    <template v-if="item.icon" #icon>
      <component :is="item.icon" v-if="item.icon.startsWith('icon-')" />
      <span v-else>{{ item.icon }}</span>
    </template>
    {{ item.title }}
  </a-menu-item>

  <!-- 有子菜单的父节点 -->
  <a-sub-menu v-else :key="fullPath">
    <template v-if="item.icon" #icon>
      <component :is="item.icon" v-if="item.icon.startsWith('icon-')" />
      <span v-else>{{ item.icon }}</span>
    </template>

    <template #title>{{ item.title }}</template>

    <sidebar-item 
      v-for="child in item.children" 
      :key="child.id || child.path" 
      :item="child" 
      :parent-path="fullPath" 
    />
  </a-sub-menu>
</template>

<script setup>
import SidebarItem from '.'
import { defineProps, computed } from 'vue'

const props = defineProps({
  item: Object,
  parentPath: String
})

const fullPath = computed(() => {
  if (!props.item.path) {
    return props.parentPath || ''
  }
  
  let path = props.item.path.startsWith('/') 
    ? props.item.path 
    : `/${props.item.path}`
  
  if (props.parentPath) {
    path = props.parentPath + path
  }
  
  return path.replace(/\/+/g, '/')
})

// 生成路由名称（用于命名路由跳转）
const routeName = computed(() => {
  if (!props.item.path) {
    return `menu_${props.item.id}`
  }
  return props.item.path.replace(/\//g, '_').replace(/^_/, '') || `menu_${props.item.id}`
})
</script>
