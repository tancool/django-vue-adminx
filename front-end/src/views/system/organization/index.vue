<template>
  <div class="organization-management">
    <a-card>
      <template #title>
        <a-typography-title :heading="4">组织管理</a-typography-title>
      </template>

      <!-- 工具栏 -->
      <div class="toolbar">
        <a-space>
          <a-input-search
            v-model="searchText"
            placeholder="搜索组织名称或编码"
            style="width: 300px"
            @search="handleSearch"
            @clear="handleSearch"
            allow-clear
          />
          <a-button type="primary" @click="handleCreate">
            <template #icon>
              <icon-plus />
            </template>
            新增组织
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
          {{ record.parent?.name || '-' }}
        </template>

        <template #leader="{ record }">
          {{ record.leader?.username || '-' }}
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
        <a-form-item field="name" label="组织名称">
          <a-input v-model="formData.name" placeholder="请输入组织名称" />
        </a-form-item>

        <a-form-item field="code" label="组织编码">
          <a-input v-model="formData.code" placeholder="请输入组织编码" />
        </a-form-item>

        <a-form-item field="parent" label="上级组织">
          <a-select
            v-model="formData.parent"
            placeholder="请选择上级组织（可选）"
            allow-clear
            :loading="orgLoading"
          >
            <a-option
              v-for="org in orgList"
              :key="org.id"
              :value="org.id"
              :disabled="org.id === formData.id"
            >
              {{ org.name }}
            </a-option>
          </a-select>
        </a-form-item>

        <a-form-item field="order" label="排序">
          <a-input-number v-model="formData.order" :min="0" placeholder="请输入排序值" />
        </a-form-item>

        <a-form-item field="leader" label="负责人">
          <a-input
            v-model="formData.leader"
            placeholder="请输入负责人用户ID（可选）"
            allow-clear
          />
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
  getOrganizationList,
  getOrganizationDetail,
  createOrganization,
  updateOrganization,
  deleteOrganization
} from '@/api/organization'

const columns = [
  { title: 'ID', dataIndex: 'id', width: 80 },
  { title: '组织名称', dataIndex: 'name' },
  { title: '组织编码', dataIndex: 'code' },
  { title: '上级组织', dataIndex: 'parent', slotName: 'parent' },
  { title: '负责人', dataIndex: 'leader', slotName: 'leader' },
  { title: '排序', dataIndex: 'order', width: 80 },
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
const formTitle = ref('新增组织')
const formRef = ref()
const formData = reactive({
  id: null,
  name: '',
  code: '',
  parent: null,
  order: 0,
  leader: null,
  is_active: true
})

const formRules = {
  name: [{ required: true, message: '请输入组织名称' }],
  code: [{ required: true, message: '请输入组织编码' }]
}

const orgList = ref([])
const orgLoading = ref(false)

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
    const res = await getOrganizationList(params)
    tableData.value = res.results || res.data || []
    pagination.total = res.count || res.total || 0
  } catch (e) {
    Message.error('获取列表失败')
  } finally {
    loading.value = false
  }
}

// 加载组织列表（用于父组织选择）
const loadOrgList = async () => {
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
  formTitle.value = '新增组织'
  Object.assign(formData, {
    id: null,
    name: '',
    code: '',
    parent: null,
    order: 0,
    leader: null,
    is_active: true
  })
  formVisible.value = true
}

// 编辑
const handleEdit = async (record) => {
  formTitle.value = '编辑组织'
  try {
    const res = await getOrganizationDetail(record.id)
    Object.assign(formData, {
      id: res.id,
      name: res.name,
      code: res.code,
      parent: res.parent || null,
      order: res.order || 0,
      leader: res.leader || null,
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
    content: `确定要删除组织"${record.name}"吗？`,
    onOk: async () => {
      try {
        await deleteOrganization(record.id)
        Message.success('删除成功')
        fetchData()
        loadOrgList() // 刷新组织列表
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
      parent: formData.parent || null,
      order: formData.order,
      leader: formData.leader || null,
      is_active: formData.is_active
    }

    if (formData.id) {
      await updateOrganization(formData.id, data)
      Message.success('更新成功')
    } else {
      await createOrganization(data)
      Message.success('创建成功')
    }

    formVisible.value = false
    fetchData()
    loadOrgList() // 刷新组织列表
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
  loadOrgList()
})
</script>

<style scoped>
.organization-management {
  padding: 20px;
}

.toolbar {
  margin-bottom: 16px;
}
</style>
