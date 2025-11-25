<template>
  <div class="pve-server">
    <a-card>
      <template #title>
        <a-typography-title :heading="4">PVE服务器管理</a-typography-title>
      </template>

      <!-- 工具栏 -->
      <div class="toolbar">
        <a-space>
          <a-input-search
            v-model="searchText"
            placeholder="搜索服务器名称或地址"
            style="width: 300px"
            @search="handleSearch"
            @clear="handleSearch"
            allow-clear
          />
          <a-button type="primary" @click="handleCreate">
            <template #icon>
              <icon-plus />
            </template>
            新增服务器
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


        <template #actions="{ record }">
          <a-button type="text" size="small" @click="handleTestConnection(record)">测试连接</a-button>
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
      :width="700"
    >
      <a-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        layout="vertical"
      >
        <a-form-item field="name" label="服务器名称">
          <a-input
            v-model="formData.name"
            placeholder="请输入服务器名称"
          />
        </a-form-item>

        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item field="host" label="服务器地址">
              <a-input
                v-model="formData.host"
                placeholder="如：192.168.1.100"
              />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item field="port" label="端口">
              <a-input-number
                v-model="formData.port"
                :min="1"
                :max="65535"
                placeholder="默认8006"
              />
            </a-form-item>
          </a-col>
        </a-row>

        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item field="token_id" label="Token ID">
              <a-input
                v-model="formData.token_id"
                placeholder="API Token ID"
              />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item field="token_secret" label="Token Secret">
              <a-input-password
                v-model="formData.token_secret"
                placeholder="API Token Secret"
              />
            </a-form-item>
          </a-col>
        </a-row>

        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item field="verify_ssl" label="验证SSL">
              <a-switch v-model="formData.verify_ssl" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item field="is_active" label="是否启用">
              <a-switch v-model="formData.is_active" />
            </a-form-item>
          </a-col>
        </a-row>

        <a-form-item field="remark" label="备注">
          <a-textarea
            v-model="formData.remark"
            placeholder="请输入备注信息"
            :auto-size="{ minRows: 2, maxRows: 4 }"
          />
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
  getPVEServers,
  getPVEServer,
  createPVEServer,
  updatePVEServer,
  deletePVEServer,
  testPVEServerConnection
} from '@/api/pve'

const columns = [
  { title: 'ID', dataIndex: 'id', width: 80 },
  { title: '服务器名称', dataIndex: 'name', width: 150 },
  { title: '服务器地址', dataIndex: 'host', width: 150 },
  { title: '端口', dataIndex: 'port', width: 100 },
  { title: 'Token ID', dataIndex: 'token_id', width: 150 },
  { title: '状态', dataIndex: 'is_active', slotName: 'is_active', width: 100 },
  { title: '创建时间', dataIndex: 'created_at', width: 180 },
  { title: '操作', slotName: 'actions', width: 200, fixed: 'right' }
]

const loading = ref(false)
const searchText = ref('')
const tableData = ref([])
const formVisible = ref(false)
const formTitle = ref('新增服务器')
const isEdit = ref(false)

const pagination = reactive({
  current: 1,
  pageSize: 20,
  total: 0,
  showTotal: true,
  showPageSize: true
})

const formData = reactive({
  id: null,
  name: '',
  host: '',
  port: 8006,
  token_id: '',
  token_secret: '',
  verify_ssl: false,
  is_active: true,
  remark: ''
})

const formRules = {
  name: [{ required: true, message: '请输入服务器名称' }],
  host: [{ required: true, message: '请输入服务器地址' }],
  port: [{ required: true, message: '请输入端口' }],
  token_id: [{ required: true, message: '请输入Token ID' }],
  token_secret: [{ required: true, message: '请输入Token Secret' }]
}

const formRef = ref(null)

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
    const res = await getPVEServers(params)
    if (Array.isArray(res)) {
      tableData.value = res
      pagination.total = res.length
    } else if (res.results) {
      tableData.value = res.results
      pagination.total = res.count || 0
    } else {
      tableData.value = []
      pagination.total = 0
    }
  } catch (error) {
    Message.error('获取服务器列表失败：' + (error.message || '未知错误'))
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.current = 1
  fetchData()
}

const handlePageChange = (page) => {
  pagination.current = page
  fetchData()
}

const handlePageSizeChange = (pageSize) => {
  pagination.pageSize = pageSize
  pagination.current = 1
  fetchData()
}

const handleCreate = () => {
  isEdit.value = false
  formTitle.value = '新增服务器'
  Object.assign(formData, {
    id: null,
    name: '',
    host: '',
    port: 8006,
    token_id: '',
    token_secret: '',
    verify_ssl: false,
    is_active: true,
    remark: ''
  })
  formVisible.value = true
}

const handleEdit = async (record) => {
  isEdit.value = true
  formTitle.value = '编辑服务器'
  try {
    const res = await getPVEServer(record.id)
    Object.assign(formData, {
      id: res.id,
      name: res.name,
      host: res.host,
      port: res.port,
      token_id: res.token_id,
      token_secret: '', // 不显示secret
      verify_ssl: res.verify_ssl,
      is_active: res.is_active,
      remark: res.remark || ''
    })
    formVisible.value = true
  } catch (error) {
    Message.error('获取服务器详情失败：' + (error.message || '未知错误'))
  }
}

const handleDelete = (record) => {
  Modal.confirm({
    title: '确认删除',
    content: `确定要删除服务器 "${record.name}" 吗？`,
    onOk: async () => {
      try {
        await deletePVEServer(record.id)
        Message.success('删除成功')
        fetchData()
      } catch (error) {
        Message.error('删除失败：' + (error.message || '未知错误'))
      }
    }
  })
}

const handleTestConnection = async (record) => {
  try {
    loading.value = true
    const res = await testPVEServerConnection(record.id)
    if (res.success) {
      Message.success(`连接成功！版本：${res.version?.version || '未知'}`)
    } else {
      Message.error('连接失败：' + res.message)
    }
  } catch (error) {
    Message.error('测试连接失败：' + (error.message || '未知错误'))
  } finally {
    loading.value = false
  }
}

const handleSubmit = async () => {
  try {
    await formRef.value.validate()
    
    const submitData = { ...formData }
    // 编辑时不发送空的token_secret（如果用户没有修改）
    if (isEdit.value && !submitData.token_secret) {
      delete submitData.token_secret
    }
    
    if (isEdit.value && formData.id) {
      await updatePVEServer(formData.id, submitData)
      Message.success('更新成功')
    } else {
      await createPVEServer(submitData)
      Message.success('创建成功')
    }
    
    formVisible.value = false
    fetchData()
  } catch (error) {
    if (error.errors) {
      return false
    }
    Message.error((isEdit.value ? '更新' : '创建') + '失败：' + (error.message || '未知错误'))
    return false
  }
}

const handleCancel = () => {
  formVisible.value = false
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.pve-server {
  padding: 20px;
}

.toolbar {
  margin-bottom: 16px;
}
</style>

