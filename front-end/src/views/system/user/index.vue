<template>
  <div class="user-management">
    <a-card>
      <template #title>
        <a-typography-title :heading="4">用户管理</a-typography-title>
      </template>

      <!-- 工具栏 -->
      <div class="toolbar">
        <a-space>
          <a-input-search
            v-model="searchText"
            placeholder="搜索用户名、邮箱或姓名"
            style="width: 300px"
            @search="handleSearch"
            @clear="handleSearch"
            allow-clear
          />
          <a-button type="primary" @click="handleCreate">
            <template #icon>
              <icon-plus />
            </template>
            新增用户
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
        <template #is_active="{ record }">
          <a-tag :color="record.is_active ? 'green' : 'red'">
            {{ record.is_active ? '启用' : '禁用' }}
          </a-tag>
        </template>

        <template #is_staff="{ record }">
          <a-tag :color="record.is_staff ? 'blue' : 'gray'">
            {{ record.is_staff ? '是' : '否' }}
          </a-tag>
        </template>

        <template #is_superuser="{ record }">
          <a-tag :color="record.is_superuser ? 'red' : 'gray'">
            {{ record.is_superuser ? '是' : '否' }}
          </a-tag>
        </template>

        <template #date_joined="{ record }">
          {{ formatDate(record.date_joined) }}
        </template>

        <template #last_login="{ record }">
          {{ record.last_login ? formatDate(record.last_login) : '-' }}
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
      @before-ok="handleSubmit"
      @cancel="handleCancel"
      :width="600"
    >
      <a-form
        ref="formRef"
        :model="formData"
        :rules="getFormRules()"
        layout="vertical"
      >
        <a-form-item field="username" label="用户名">
          <a-input v-model="formData.username" placeholder="请输入用户名" />
        </a-form-item>

        <a-form-item field="email" label="邮箱">
          <a-input v-model="formData.email" placeholder="请输入邮箱" type="email" />
        </a-form-item>

        <a-form-item v-if="!formData.id" field="password" label="密码">
          <a-input-password v-model="formData.password" placeholder="请输入密码（至少6位）" />
        </a-form-item>

        <a-form-item v-if="formData.id" field="password" label="密码（留空不修改）">
          <a-input-password v-model="formData.password" placeholder="留空则不修改密码" />
        </a-form-item>

        <a-form-item field="first_name" label="名">
          <a-input v-model="formData.first_name" placeholder="请输入名" />
        </a-form-item>

        <a-form-item field="last_name" label="姓">
          <a-input v-model="formData.last_name" placeholder="请输入姓" />
        </a-form-item>

        <a-form-item field="is_active" label="是否启用">
          <a-switch v-model="formData.is_active" />
        </a-form-item>

        <a-form-item field="is_staff" label="是否员工">
          <a-switch v-model="formData.is_staff" />
        </a-form-item>

        <a-form-item field="is_superuser" label="是否超级管理员">
          <a-switch v-model="formData.is_superuser" />
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
  getUserList,
  getUserDetail,
  createUser,
  updateUser,
  deleteUser
} from '@/api/user-management'

const columns = [
  { title: 'ID', dataIndex: 'id', width: 80 },
  { title: '用户名', dataIndex: 'username' },
  { title: '邮箱', dataIndex: 'email' },
  { title: '姓名', dataIndex: 'first_name', render: ({ record }) => `${record.first_name || ''} ${record.last_name || ''}`.trim() || '-' },
  { title: '启用', dataIndex: 'is_active', slotName: 'is_active', width: 100 },
  { title: '员工', dataIndex: 'is_staff', slotName: 'is_staff', width: 100 },
  { title: '超级管理员', dataIndex: 'is_superuser', slotName: 'is_superuser', width: 120 },
  { title: '注册时间', dataIndex: 'date_joined', slotName: 'date_joined', width: 180 },
  { title: '最后登录', dataIndex: 'last_login', slotName: 'last_login', width: 180 },
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
const formTitle = ref('新增用户')
const formRef = ref()
const formData = reactive({
  id: null,
  username: '',
  email: '',
  password: '',
  first_name: '',
  last_name: '',
  is_active: true,
  is_staff: false,
  is_superuser: false
})

// 动态表单验证规则
const getFormRules = () => {
  const rules = {
    username: [{ required: true, message: '请输入用户名' }],
    email: [{ required: true, type: 'email', message: '请输入有效的邮箱地址' }]
  }
  
  // 新增时密码必填，编辑时可选
  if (!formData.id) {
    rules.password = [
      { required: true, message: '请输入密码' },
      { min: 6, message: '密码至少6位' }
    ]
  } else {
    rules.password = [
      {
        validator: (value, cb) => {
          // 编辑时，如果填写了密码，则验证长度
          if (value && value.length < 6) {
            cb('密码至少6位')
          } else {
            cb()
          }
        }
      }
    ]
  }
  
  return rules
}

// 格式化日期
const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}

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
    const res = await getUserList(params)
    tableData.value = res.results || res.data || []
    pagination.total = res.count || res.total || 0
  } catch (e) {
    Message.error('获取列表失败')
  } finally {
    loading.value = false
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
  formTitle.value = '新增用户'
  Object.assign(formData, {
    id: null,
    username: '',
    email: '',
    password: '',
    first_name: '',
    last_name: '',
    is_active: true,
    is_staff: false,
    is_superuser: false
  })
  formVisible.value = true
}

// 编辑
const handleEdit = async (record) => {
  formTitle.value = '编辑用户'
  try {
    const res = await getUserDetail(record.id)
    Object.assign(formData, {
      id: res.id,
      username: res.username,
      email: res.email || '',
      password: '', // 编辑时不显示密码
      first_name: res.first_name || '',
      last_name: res.last_name || '',
      is_active: res.is_active !== undefined ? res.is_active : true,
      is_staff: res.is_staff || false,
      is_superuser: res.is_superuser || false
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
    content: `确定要删除用户"${record.username}"吗？`,
    onOk: async () => {
      try {
        await deleteUser(record.id)
        Message.success('删除成功')
        fetchData()
      } catch (e) {
        Message.error('删除失败')
      }
    }
  })
}

// 提交表单（使用 before-ok，需要返回 Promise 或 false 来阻止关闭）
const handleSubmit = async () => {
  console.log('handleSubmit 被调用', formData)
  
  // Arco Design 的表单验证：验证失败会抛出错误，成功返回 undefined
  try {
    await formRef.value?.validate()
    console.log('表单验证通过')
  } catch (error) {
    console.log('表单验证失败:', error)
    return false // 验证失败，阻止关闭
  }

  try {
    const data = {
      username: formData.username,
      email: formData.email,
      first_name: formData.first_name || '',
      last_name: formData.last_name || '',
      is_active: formData.is_active,
      is_staff: formData.is_staff,
      is_superuser: formData.is_superuser
    }

    if (formData.id) {
      // 编辑：只有提供了密码才发送
      console.log('编辑用户，ID:', formData.id)
      if (formData.password && formData.password.trim()) {
        data.password = formData.password
      }
      console.log('调用 updateUser API，数据:', data)
      await updateUser(formData.id, data)
      console.log('updateUser 成功')
      Message.success('更新成功')
    } else {
      // 新增：密码必填
      console.log('新增用户，数据:', data)
      if (!formData.password || formData.password.trim().length < 6) {
        Message.error('密码至少6位')
        return false // 阻止关闭
      }
      data.password = formData.password
      console.log('调用 createUser API，数据:', data)
      await createUser(data)
      console.log('createUser 成功')
      Message.success('创建成功')
    }

    formVisible.value = false
    fetchData()
    return true // 允许关闭
  } catch (e) {
    console.error('提交失败:', e)
    const errorMsg = e.response?.data?.detail || e.response?.data?.message || (formData.id ? '更新失败' : '创建失败')
    Message.error(errorMsg)
    return false // 错误时阻止关闭
  }
}

// 取消
const handleCancel = () => {
  formVisible.value = false
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.user-management {
  padding: 20px;
}

.toolbar {
  margin-bottom: 16px;
}
</style>
