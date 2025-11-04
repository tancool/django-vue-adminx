<template>
  <div class="menu-management">
    <a-card>
      <template #title>
        <a-typography-title :heading="4">菜单管理</a-typography-title>
      </template>

      <!-- 工具栏 -->
      <div class="toolbar">
        <a-space>
          <a-input-search
            v-model="searchText"
            placeholder="搜索菜单名称、路径或组件"
            style="width: 300px"
            @search="handleSearch"
            @clear="handleSearch"
            allow-clear
          />
          <a-button type="primary" @click="handleCreate">
            <template #icon>
              <icon-plus />
            </template>
            新增菜单
          </a-button>
        </a-space>
      </div>

      <!-- 表格 -->
      <a-table
        :columns="columns"
        :data="tableData"
        :loading="loading"
        :pagination="pagination"
        @page-change="handlePageChange"
        @page-size-change="handlePageSizeChange"
        :bordered="false"
        :hoverable="true"
        style="margin-top: 16px"
      >
        <template #parent="{ record }">
          {{ record.parent?.title || '-' }}
        </template>

        <template #is_hidden="{ record }">
          <a-tag :color="record.is_hidden ? 'red' : 'green'">
            {{ record.is_hidden ? '隐藏' : '显示' }}
          </a-tag>
        </template>

        <template #actions="{ record }">
          <a-button type="text" size="small" @click="handleEdit(record)">编辑</a-button>
          <a-button type="text" size="small" status="danger" @click="handleDelete(record)">删除</a-button>
        </template>
      </a-table>
    </a-card>

    <!-- 表单对话框 -->
    <a-modal
      v-model:visible="formVisible"
      :title="formTitle"
      @ok="handleSubmit"
      @cancel="handleCancel"
      :width="600"
    >
      <a-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        layout="vertical"
      >
        <a-form-item field="title" label="菜单名称">
          <a-input v-model="formData.title" placeholder="请输入菜单名称" />
        </a-form-item>

        <a-form-item field="path" label="路由路径">
          <a-input v-model="formData.path" placeholder="请输入路由路径，如：/system/user" />
        </a-form-item>

        <a-form-item field="component" label="组件路径">
          <a-input v-model="formData.component" placeholder="请输入组件路径，如：system/user/index" />
        </a-form-item>

        <a-form-item field="icon" label="图标">
          <a-input v-model="formData.icon" placeholder="请输入图标名称，如：User" />
        </a-form-item>

        <a-form-item field="parent" label="父菜单">
          <a-select
            v-model="formData.parent"
            placeholder="请选择父菜单（可选）"
            allow-clear
            :loading="menuLoading"
          >
            <a-option
              v-for="menu in menuList"
              :key="menu.id"
              :value="menu.id"
            >
              {{ menu.title }}
            </a-option>
          </a-select>
        </a-form-item>

        <a-form-item field="order" label="排序">
          <a-input-number v-model="formData.order" :min="0" placeholder="请输入排序值" />
        </a-form-item>

        <a-form-item field="is_hidden" label="是否隐藏">
          <a-switch v-model="formData.is_hidden" />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { Message, Modal } from '@arco-design/web-vue'
import { IconPlus } from '@arco-design/web-vue/es/icon'
import {
  getMenuList,
  getMenuDetail,
  createMenu,
  updateMenu,
  deleteMenu
} from '@/api/menu'

const columns = [
  { title: 'ID', dataIndex: 'id', width: 80 },
  { title: '菜单名称', dataIndex: 'title' },
  { title: '路由路径', dataIndex: 'path' },
  { title: '组件路径', dataIndex: 'component' },
  { title: '图标', dataIndex: 'icon' },
  { title: '父菜单', dataIndex: 'parent', slotName: 'parent' },
  { title: '排序', dataIndex: 'order', width: 80 },
  { title: '状态', dataIndex: 'is_hidden', slotName: 'is_hidden', width: 100 },
  { title: '操作', slotName: 'actions', width: 150, fixed: 'right' }
]

const searchText = ref('')
const loading = ref(false)
const tableData = ref([])
const pagination = reactive({
  current: 1,
  pageSize: 20,
  total: 0,
  showTotal: true,
  showPageSize: true
})

const formVisible = ref(false)
const formTitle = ref('新增菜单')
const formRef = ref()
const formData = reactive({
  id: null,
  title: '',
  path: '',
  component: '',
  icon: '',
  parent: null,
  order: 0,
  is_hidden: false
})

const formRules = {
  title: [{ required: true, message: '请输入菜单名称' }],
  path: [{ required: true, message: '请输入路由路径' }]
}

const menuList = ref([])
const menuLoading = ref(false)

// 获取列表数据
const fetchData = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.current,
      page_size: pagination.pageSize
    }
    if (searchText.value) {
      params.search = searchText.value
    }
    const res = await getMenuList(params)
    tableData.value = res.results || res.data || []
    pagination.total = res.count || res.total || 0
  } catch (e) {
    Message.error('获取列表失败')
  } finally {
    loading.value = false
  }
}

// 加载菜单列表（用于父菜单选择）
const loadMenuList = async () => {
  menuLoading.value = true
  try {
    const res = await getMenuList()
    menuList.value = res.results || res.data || []
  } catch (e) {
    console.error('加载菜单列表失败:', e)
  } finally {
    menuLoading.value = false
  }
}

// 搜索
const handleSearch = () => {
  pagination.current = 1
  fetchData()
}

// 分页
const handlePageChange = (page) => {
  pagination.current = page
  fetchData()
}

const handlePageSizeChange = (pageSize) => {
  pagination.pageSize = pageSize
  pagination.current = 1
  fetchData()
}

// 新增
const handleCreate = () => {
  formTitle.value = '新增菜单'
  Object.assign(formData, {
    id: null,
    title: '',
    path: '',
    component: '',
    icon: '',
    parent: null,
    order: 0,
    is_hidden: false
  })
  formVisible.value = true
}

// 编辑
const handleEdit = async (record) => {
  formTitle.value = '编辑菜单'
  try {
    const res = await getMenuDetail(record.id)
    Object.assign(formData, {
      id: res.id,
      title: res.title,
      path: res.path || '',
      component: res.component || '',
      icon: res.icon || '',
      parent: res.parent || null,
      order: res.order || 0,
      is_hidden: res.is_hidden || false
    })
    formVisible.value = true
  } catch (e) {
    Message.error('获取详情失败')
  }
}

// 删除
const handleDelete = (record) => {
  Modal.confirm({
    title: '确认删除',
    content: `确定要删除菜单"${record.title}"吗？`,
    onOk: async () => {
      try {
        await deleteMenu(record.id)
        Message.success('删除成功')
        fetchData()
      } catch (e) {
        Message.error('删除失败')
      }
    }
  })
}

// 提交表单
const handleSubmit = async () => {
  const valid = await formRef.value?.validate()
  if (!valid) return

  try {
    const data = {
      title: formData.title,
      path: formData.path,
      component: formData.component,
      icon: formData.icon,
      parent: formData.parent || null,
      order: formData.order,
      is_hidden: formData.is_hidden
    }

    if (formData.id) {
      await updateMenu(formData.id, data)
      Message.success('更新成功')
    } else {
      await createMenu(data)
      Message.success('创建成功')
    }

    formVisible.value = false
    fetchData()
    loadMenuList() // 刷新菜单列表
  } catch (e) {
    Message.error(formData.id ? '更新失败' : '创建失败')
  }
}

// 取消
const handleCancel = () => {
  formVisible.value = false
}

onMounted(() => {
  fetchData()
  loadMenuList()
})
</script>

<style scoped>
.menu-management {
  padding: 20px;
}

.toolbar {
  margin-bottom: 16px;
}
</style>
