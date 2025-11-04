<template>
  <div class="role-management">
    <a-card>
      <template #title>
        <a-typography-title :heading="4">角色管理</a-typography-title>
      </template>

      <!-- 工具栏 -->
      <div class="toolbar">
        <a-space>
          <a-input-search
            v-model="searchText"
            placeholder="搜索角色名称或编码"
            style="width: 300px"
            @search="handleSearch"
            @clear="handleSearch"
            allow-clear
          />
          <a-button type="primary" @click="handleCreate">
            <template #icon>
              <icon-plus />
            </template>
            新增角色
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
        <template #data_scope="{ record }">
          <a-tag :color="getDataScopeColor(record.data_scope)">
            {{ getDataScopeText(record.data_scope) }}
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
        <a-form-item field="name" label="角色名称">
          <a-input v-model="formData.name" placeholder="请输入角色名称" />
        </a-form-item>

        <a-form-item field="code" label="角色编码">
          <a-input v-model="formData.code" placeholder="请输入角色编码" />
        </a-form-item>

        <a-form-item field="description" label="描述">
          <a-textarea
            v-model="formData.description"
            placeholder="请输入描述"
            :auto-size="{ minRows: 3, maxRows: 5 }"
          />
        </a-form-item>

        <a-form-item field="data_scope" label="数据范围">
          <a-select v-model="formData.data_scope" placeholder="请选择数据范围">
            <a-option value="ALL">全部数据</a-option>
            <a-option value="DEPT">本部门</a-option>
            <a-option value="DEPT_AND_SUB">本部门及下级</a-option>
            <a-option value="SELF">仅本人</a-option>
            <a-option value="CUSTOM">自定义组织</a-option>
          </a-select>
        </a-form-item>

        <a-form-item v-if="formData.data_scope === 'CUSTOM'" field="custom_data_organizations" label="自定义组织">
          <a-select
            v-model="formData.custom_data_organizations"
            placeholder="请选择组织"
            multiple
            :loading="orgLoading"
          >
            <a-option
              v-for="org in orgList"
              :key="org.id"
              :value="org.id"
            >
              {{ org.name }}
            </a-option>
          </a-select>
        </a-form-item>

        <a-form-item field="permissions" label="权限">
          <a-select
            v-model="formData.permissions"
            placeholder="请选择权限"
            multiple
            :loading="permLoading"
            :max-tag-count="3"
          >
            <a-option
              v-for="perm in permList"
              :key="perm.id"
              :value="perm.id"
            >
              {{ perm.name }} ({{ perm.code }})
            </a-option>
          </a-select>
        </a-form-item>

        <a-form-item field="menus" label="菜单">
          <a-select
            v-model="formData.menus"
            placeholder="请选择菜单"
            multiple
            :loading="menuLoading"
            :max-tag-count="3"
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
      </a-form>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { Message, Modal } from '@arco-design/web-vue'
import { IconPlus } from '@arco-design/web-vue/es/icon'
import {
  getRoleList,
  getRoleDetail,
  createRole,
  updateRole,
  deleteRole
} from '@/api/role'
import { getPermissionList } from '@/api/permission'
import { getMenuList } from '@/api/menu'
import { getOrganizationList } from '@/api/organization'

const columns = [
  { title: 'ID', dataIndex: 'id', width: 80 },
  { title: '角色名称', dataIndex: 'name' },
  { title: '角色编码', dataIndex: 'code' },
  { title: '描述', dataIndex: 'description', ellipsis: true },
  { title: '数据范围', dataIndex: 'data_scope', slotName: 'data_scope' },
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
const formTitle = ref('新增角色')
const formRef = ref()
const formData = reactive({
  id: null,
  name: '',
  code: '',
  description: '',
  data_scope: 'SELF',
  custom_data_organizations: [],
  permissions: [],
  menus: []
})

const formRules = {
  name: [{ required: true, message: '请输入角色名称' }],
  code: [{ required: true, message: '请输入角色编码' }],
  data_scope: [{ required: true, message: '请选择数据范围' }]
}

const orgList = ref([])
const orgLoading = ref(false)
const permList = ref([])
const permLoading = ref(false)
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
    const res = await getRoleList(params)
    tableData.value = res.results || res.data || []
    pagination.total = res.count || res.total || 0
  } catch (e) {
    Message.error('获取列表失败')
  } finally {
    loading.value = false
  }
}

// 加载下拉选项数据
const loadOptions = async () => {
  // 加载权限列表
  permLoading.value = true
  try {
    const res = await getPermissionList()
    permList.value = res.results || res.data || []
  } catch (e) {
    console.error('加载权限列表失败:', e)
  } finally {
    permLoading.value = false
  }

  // 加载菜单列表
  menuLoading.value = true
  try {
    const res = await getMenuList()
    menuList.value = res.results || res.data || []
  } catch (e) {
    console.error('加载菜单列表失败:', e)
  } finally {
    menuLoading.value = false
  }

  // 加载组织列表
  orgLoading.value = true
  try {
    const res = await getOrganizationList()
    orgList.value = res.results || res.data || []
  } catch (e) {
    console.error('加载组织列表失败:', e)
  } finally {
    orgLoading.value = false
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
  formTitle.value = '新增角色'
  Object.assign(formData, {
    id: null,
    name: '',
    code: '',
    description: '',
    data_scope: 'SELF',
    custom_data_organizations: [],
    permissions: [],
    menus: []
  })
  formVisible.value = true
}

// 编辑
const handleEdit = async (record) => {
  formTitle.value = '编辑角色'
  try {
    const res = await getRoleDetail(record.id)
    Object.assign(formData, {
      id: res.id,
      name: res.name,
      code: res.code,
      description: res.description || '',
      data_scope: res.data_scope || 'SELF',
      custom_data_organizations: res.custom_data_organizations || [],
      permissions: res.permissions || [],
      menus: res.menus || []
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
    content: `确定要删除角色"${record.name}"吗？`,
    onOk: async () => {
      try {
        await deleteRole(record.id)
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
      description: formData.description,
      data_scope: formData.data_scope,
      custom_data_organizations: formData.custom_data_organizations,
      permissions: formData.permissions,
      menus: formData.menus
    }

    if (formData.id) {
      await updateRole(formData.id, data)
      Message.success('更新成功')
    } else {
      await createRole(data)
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

// 数据范围文本
const getDataScopeText = (scope) => {
  const map = {
    ALL: '全部数据',
    DEPT: '本部门',
    DEPT_AND_SUB: '本部门及下级',
    SELF: '仅本人',
    CUSTOM: '自定义组织'
  }
  return map[scope] || scope
}

// 数据范围颜色
const getDataScopeColor = (scope) => {
  const map = {
    ALL: 'red',
    DEPT: 'blue',
    DEPT_AND_SUB: 'green',
    SELF: 'orange',
    CUSTOM: 'purple'
  }
  return map[scope] || 'gray'
}

onMounted(() => {
  fetchData()
  loadOptions()
})
</script>

<style scoped>
.role-management {
  padding: 20px;
}

.toolbar {
  margin-bottom: 16px;
}
</style>
