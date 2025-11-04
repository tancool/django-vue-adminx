<template>
  <div class="permission-management">
    <a-card>
      <template #title>
        <a-typography-title :heading="4">权限管理</a-typography-title>
      </template>

      <!-- 工具栏 -->
      <div class="toolbar">
        <a-space>
          <a-input-search
            v-model="searchText"
            placeholder="搜索权限名称、编码或URL"
            style="width: 300px"
            @search="handleSearch"
            @clear="handleSearch"
            allow-clear
          />
          <a-button type="primary" @click="handleCreate">
            <template #icon>
              <icon-plus />
            </template>
            新增权限
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
        <template #http_method="{ record }">
          <a-tag :color="getMethodColor(record.http_method)">
            {{ record.http_method }}
          </a-tag>
        </template>

        <template #menu="{ record }">
          {{ record.menu?.title || '-' }}
        </template>

        <template #is_active="{ record }">
          <a-tag :color="record.is_active ? 'green' : 'red'">
            {{ record.is_active ? '启用' : '禁用' }}
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
        <a-form-item field="name" label="权限名称">
          <a-input v-model="formData.name" placeholder="请输入权限名称" />
        </a-form-item>

        <a-form-item field="code" label="权限编码">
          <a-input v-model="formData.code" placeholder="请输入权限编码，如：user:list" />
        </a-form-item>

        <a-form-item field="http_method" label="HTTP方法">
          <a-select v-model="formData.http_method" placeholder="请选择HTTP方法">
            <a-option value="GET">GET</a-option>
            <a-option value="POST">POST</a-option>
            <a-option value="PUT">PUT</a-option>
            <a-option value="PATCH">PATCH</a-option>
            <a-option value="DELETE">DELETE</a-option>
            <a-option value="ANY">ANY</a-option>
          </a-select>
        </a-form-item>

        <a-form-item field="url_pattern" label="URL匹配">
          <a-input v-model="formData.url_pattern" placeholder="请输入URL匹配模式，如：/api/rbac/users/" />
        </a-form-item>

        <a-form-item field="menu" label="所属菜单">
          <a-select
            v-model="formData.menu"
            placeholder="请选择所属菜单（可选）"
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

        <a-form-item field="is_active" label="是否启用">
          <a-switch v-model="formData.is_active" />
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
  getPermissionList,
  getPermissionDetail,
  createPermission,
  updatePermission,
  deletePermission
} from '@/api/permission'
import { getMenuList } from '@/api/menu'

const columns = [
  { title: 'ID', dataIndex: 'id', width: 80 },
  { title: '权限名称', dataIndex: 'name' },
  { title: '权限编码', dataIndex: 'code' },
  { title: 'HTTP方法', dataIndex: 'http_method', slotName: 'http_method', width: 100 },
  { title: 'URL匹配', dataIndex: 'url_pattern', ellipsis: true },
  { title: '所属菜单', dataIndex: 'menu', slotName: 'menu' },
  { title: '状态', dataIndex: 'is_active', slotName: 'is_active', width: 100 },
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
const formTitle = ref('新增权限')
const formRef = ref()
const formData = reactive({
  id: null,
  name: '',
  code: '',
  http_method: 'ANY',
  url_pattern: '',
  menu: null,
  is_active: true
})

const formRules = {
  name: [{ required: true, message: '请输入权限名称' }],
  code: [{ required: true, message: '请输入权限编码' }],
  url_pattern: [{ required: true, message: '请输入URL匹配模式' }]
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
    const res = await getPermissionList(params)
    tableData.value = res.results || res.data || []
    pagination.total = res.count || res.total || 0
  } catch (e) {
    Message.error('获取列表失败')
  } finally {
    loading.value = false
  }
}

// 加载菜单列表
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
  formTitle.value = '新增权限'
  Object.assign(formData, {
    id: null,
    name: '',
    code: '',
    http_method: 'ANY',
    url_pattern: '',
    menu: null,
    is_active: true
  })
  formVisible.value = true
}

// 编辑
const handleEdit = async (record) => {
  formTitle.value = '编辑权限'
  try {
    const res = await getPermissionDetail(record.id)
    Object.assign(formData, {
      id: res.id,
      name: res.name,
      code: res.code,
      http_method: res.http_method || 'ANY',
      url_pattern: res.url_pattern || '',
      menu: res.menu || null,
      is_active: res.is_active !== undefined ? res.is_active : true
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
    content: `确定要删除权限"${record.name}"吗？`,
    onOk: async () => {
      try {
        await deletePermission(record.id)
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
      name: formData.name,
      code: formData.code,
      http_method: formData.http_method,
      url_pattern: formData.url_pattern,
      menu: formData.menu || null,
      is_active: formData.is_active
    }

    if (formData.id) {
      await updatePermission(formData.id, data)
      Message.success('更新成功')
    } else {
      await createPermission(data)
      Message.success('创建成功')
    }

    formVisible.value = false
    fetchData()
  } catch (e) {
    Message.error(formData.id ? '更新失败' : '创建失败')
  }
}

// 取消
const handleCancel = () => {
  formVisible.value = false
}

// HTTP方法颜色
const getMethodColor = (method) => {
  const map = {
    GET: 'blue',
    POST: 'green',
    PUT: 'orange',
    PATCH: 'purple',
    DELETE: 'red',
    ANY: 'gray'
  }
  return map[method] || 'gray'
}

onMounted(() => {
  fetchData()
  loadMenuList()
})
</script>

<style scoped>
.permission-management {
  padding: 20px;
}

.toolbar {
  margin-bottom: 16px;
}
</style>
