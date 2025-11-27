<template>
  <div class="pve-templates">
    <a-card>
      <template #title>
        <a-typography-title :heading="4">模板管理</a-typography-title>
      </template>

      <!-- 工具栏 -->
      <div class="toolbar">
        <a-space size="large" wrap>
          <div class="toolbar-field">
            <div class="label">服务器</div>
            <a-select
              v-model="filters.server_id"
              placeholder="全部服务器"
              allow-clear
              style="width: 200px"
              @change="handleFilterChange"
            >
              <a-option
                v-for="server in servers"
                :key="server.id"
                :value="server.id"
              >
                {{ server.name }}
              </a-option>
            </a-select>
          </div>
          <div class="toolbar-field">
            <div class="label">节点</div>
            <a-input
              v-model="filters.node"
              placeholder="节点名称"
              style="width: 150px"
              allow-clear
              @clear="handleFilterChange"
              @press-enter="handleFilterChange"
            />
          </div>
          <div class="toolbar-field">
            <div class="label">存储</div>
            <a-input
              v-model="filters.storage"
              placeholder="存储名称"
              style="width: 150px"
              allow-clear
              @clear="handleFilterChange"
              @press-enter="handleFilterChange"
            />
          </div>
          <div class="toolbar-field">
            <div class="label">类型</div>
            <a-select
              v-model="filters.content_type"
              placeholder="全部类型"
              style="width: 150px"
              @change="handleFilterChange"
            >
              <a-option value="all">全部类型</a-option>
              <a-option value="iso">ISO镜像</a-option>
              <a-option value="vztmpl">容器模板</a-option>
              <a-option value="backup">备份文件</a-option>
            </a-select>
          </div>
          <a-button type="primary" @click="loadTemplates" :loading="loading">
            <template #icon>
              <icon-refresh />
            </template>
            刷新
          </a-button>
          <a-button type="primary" @click="uploadModalVisible = true">
            <template #icon>
              <icon-upload />
            </template>
            上传模板
          </a-button>
        </a-space>
      </div>

      <!-- 模板表格 -->
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
        <template #server="{ record }">
          <div>
            <div style="font-weight: 500">{{ record.server_name }}</div>
            <div style="font-size: 12px; color: var(--color-text-3)">
              {{ record.server_host }}
            </div>
          </div>
        </template>

        <template #content_type="{ record }">
          <a-tag :color="getContentTypeColor(record.content)">
            {{ formatContentType(record.content) }}
          </a-tag>
        </template>

        <template #size="{ record }">
          {{ formatBytes(record.size) }}
        </template>

        <template #actions="{ record }">
          <a-space>
            <a-button type="text" size="small" @click="handleViewDetails(record)">
              详情
            </a-button>
            <a-popconfirm
              content="确定要删除此模板吗？"
              @ok="handleDelete(record)"
            >
              <a-button type="text" size="small" status="danger">
                删除
              </a-button>
            </a-popconfirm>
          </a-space>
        </template>
      </a-table>
    </a-card>

    <!-- 上传对话框 -->
    <a-modal
      v-model:visible="uploadModalVisible"
      title="上传模板"
      width="600px"
      @ok="handleUpload"
      @cancel="resetUploadForm"
    >
      <a-form :model="uploadForm" layout="vertical">
        <a-form-item field="server_id" label="服务器" required>
          <a-select
            v-model="uploadForm.server_id"
            placeholder="请选择服务器"
            @change="handleUploadServerChange"
          >
            <a-option
              v-for="server in servers"
              :key="server.id"
              :value="server.id"
            >
              {{ server.name }}
            </a-option>
          </a-select>
        </a-form-item>
        <a-form-item field="node" label="节点" required>
          <a-select
            v-model="uploadForm.node"
            placeholder="请选择节点"
            :loading="uploadNodesLoading"
            :disabled="!uploadForm.server_id"
            @change="handleUploadNodeChange"
          >
            <a-option
              v-for="node in uploadNodes"
              :key="node.value"
              :value="node.value"
            >
              {{ node.label }}
            </a-option>
          </a-select>
        </a-form-item>
        <a-form-item field="storage" label="存储" required>
          <a-select
            v-model="uploadForm.storage"
            placeholder="请选择存储"
            :loading="uploadStoragesLoading"
            :disabled="!uploadForm.node"
          >
            <a-option
              v-for="storage in uploadStorages"
              :key="storage.storage"
              :value="storage.storage"
            >
              {{ storage.storage }} ({{ storage.type }})
            </a-option>
          </a-select>
        </a-form-item>
        <a-form-item field="content_type" label="模板类型" required>
          <a-select v-model="uploadForm.content_type" placeholder="请选择类型">
            <a-option value="iso">ISO镜像</a-option>
            <a-option value="vztmpl">容器模板</a-option>
          </a-select>
        </a-form-item>
        <a-form-item field="file" label="文件" required>
          <a-upload
            v-model:file-list="uploadForm.fileList"
            :auto-upload="false"
            :limit="1"
            accept=".iso,.img,.tar.gz"
          >
            <template #upload-button>
              <a-button>
                <template #icon>
                  <icon-upload />
                </template>
                选择文件
              </a-button>
            </template>
          </a-upload>
        </a-form-item>
      </a-form>
    </a-modal>

    <!-- 详情对话框 -->
    <a-modal
      v-model:visible="detailModalVisible"
      :title="`模板详情 - ${currentTemplate?.volid || ''}`"
      width="700px"
      :footer="false"
    >
      <a-descriptions
        v-if="currentTemplate"
        :column="2"
        bordered
      >
        <a-descriptions-item label="服务器">
          {{ currentTemplate.server_name }}
        </a-descriptions-item>
        <a-descriptions-item label="节点">
          {{ currentTemplate.node }}
        </a-descriptions-item>
        <a-descriptions-item label="存储">
          {{ currentTemplate.storage }}
        </a-descriptions-item>
        <a-descriptions-item label="类型">
          <a-tag :color="getContentTypeColor(currentTemplate.content)">
            {{ formatContentType(currentTemplate.content) }}
          </a-tag>
        </a-descriptions-item>
        <a-descriptions-item label="文件大小">
          {{ formatBytes(currentTemplate.size) }}
        </a-descriptions-item>
        <a-descriptions-item label="创建时间">
          {{ formatTime(currentTemplate.ctime) }}
        </a-descriptions-item>
        <a-descriptions-item label="完整路径" :span="2">
          {{ currentTemplate.volid }}
        </a-descriptions-item>
      </a-descriptions>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { Message } from '@arco-design/web-vue'
import { IconRefresh, IconUpload } from '@arco-design/web-vue/es/icon'
import {
  getPVEServers,
  getPVEServerNodes,
  getNodeStorage,
  getStorageContent,
  uploadStorageContent
} from '@/api/pve'

const loading = ref(false)
const uploadModalVisible = ref(false)
const detailModalVisible = ref(false)
const servers = ref([])
const tableData = ref([])
const currentTemplate = ref(null)

const uploadNodesLoading = ref(false)
const uploadStoragesLoading = ref(false)
const uploadNodes = ref([])
const uploadStorages = ref([])

const filters = reactive({
  server_id: null,
  node: '',
  storage: '',
  content_type: 'all'
})

const uploadForm = reactive({
  server_id: null,
  node: null,
  storage: null,
  content_type: 'iso',
  fileList: []
})

const pagination = reactive({
  current: 1,
  pageSize: 20,
  total: 0,
  showTotal: true
})

const columns = [
  {
    title: '服务器',
    dataIndex: 'server',
    slotName: 'server',
    width: 180
  },
  {
    title: '节点',
    dataIndex: 'node',
    width: 120
  },
  {
    title: '存储',
    dataIndex: 'storage',
    width: 150
  },
  {
    title: '文件名',
    dataIndex: 'volid',
    ellipsis: true,
    tooltip: true
  },
  {
    title: '类型',
    dataIndex: 'content_type',
    slotName: 'content_type',
    width: 120
  },
  {
    title: '大小',
    dataIndex: 'size',
    slotName: 'size',
    width: 120
  },
  {
    title: '创建时间',
    dataIndex: 'ctime',
    width: 180
  },
  {
    title: '操作',
    slotName: 'actions',
    width: 150,
    fixed: 'right'
  }
]

function loadServers() {
  getPVEServers({ page_size: 200, is_active: true }).then(res => {
    const data = Array.isArray(res) ? res : res?.results || res?.data || []
    servers.value = data
  }).catch(err => {
    console.error('获取服务器列表失败:', err)
  })
}

async function loadTemplates() {
  loading.value = true
  const allTemplates = []
  
  // 获取要查询的服务器列表
  const targetServers = filters.server_id
    ? servers.value.filter(s => s.id === filters.server_id)
    : servers.value
  
  for (const server of targetServers) {
    try {
      // 获取节点列表
      const nodesRes = await getPVEServerNodes(server.id)
      const nodes = Array.isArray(nodesRes) ? nodesRes : nodesRes?.data || []
      
      for (const nodeInfo of nodes) {
        const nodeName = nodeInfo.node || nodeInfo.name
        if (filters.node && filters.node !== nodeName) {
          continue
        }
        
        try {
          // 获取存储列表
          const storagesRes = await getNodeStorage(server.id, nodeName)
          const storages = Array.isArray(storagesRes) ? storagesRes : []
          
          for (const storage of storages) {
            if (filters.storage && filters.storage !== storage.storage) {
              continue
            }
            
            // 只查询支持 ISO 和容器模板的存储
            const contentTypes = storage.content?.split(',') || []
            const hasIso = contentTypes.includes('iso')
            const hasVztmpl = contentTypes.includes('vztmpl')
            
            if (!hasIso && !hasVztmpl) {
              continue
            }
            
            try {
              // 获取 ISO 模板
              if (hasIso && (filters.content_type === 'all' || filters.content_type === 'iso')) {
                const isoRes = await getStorageContent(server.id, nodeName, storage.storage, { content: 'iso' })
                const isoList = Array.isArray(isoRes) ? isoRes : []
                isoList.forEach(item => {
                  allTemplates.push({
                    ...item,
                    server_id: server.id,
                    server_name: server.name,
                    server_host: server.host,
                    node: nodeName,
                    storage: storage.storage,
                    content: 'iso'
                  })
                })
              }
              
              // 获取容器模板
              if (hasVztmpl && (filters.content_type === 'all' || filters.content_type === 'vztmpl')) {
                const vztmplRes = await getStorageContent(server.id, nodeName, storage.storage, { content: 'vztmpl' })
                const vztmplList = Array.isArray(vztmplRes) ? vztmplRes : []
                vztmplList.forEach(item => {
                  allTemplates.push({
                    ...item,
                    server_id: server.id,
                    server_name: server.name,
                    server_host: server.host,
                    node: nodeName,
                    storage: storage.storage,
                    content: 'vztmpl'
                  })
                })
              }
            } catch (err) {
              console.warn(`获取存储 ${storage.storage} 内容失败:`, err)
            }
          }
        } catch (err) {
          console.warn(`获取节点 ${nodeName} 存储失败:`, err)
        }
      }
    } catch (err) {
      console.warn(`获取服务器 ${server.name} 节点失败:`, err)
    }
  }
  
  // 前端分页
  const start = (pagination.current - 1) * pagination.pageSize
  const end = start + pagination.pageSize
  tableData.value = allTemplates.slice(start, end)
  pagination.total = allTemplates.length
  
  loading.value = false
}

function handleFilterChange() {
  pagination.current = 1
  loadTemplates()
}

function handlePageChange(page) {
  pagination.current = page
  loadTemplates()
}

function handlePageSizeChange(size) {
  pagination.pageSize = size
  pagination.current = 1
  loadTemplates()
}

function handleViewDetails(record) {
  currentTemplate.value = record
  detailModalVisible.value = true
}

function handleDelete(record) {
  // TODO: 实现删除功能
  Message.info('删除功能待实现')
}

function handleUploadServerChange() {
  uploadForm.node = null
  uploadForm.storage = null
  uploadNodes.value = []
  uploadStorages.value = []
  
  if (!uploadForm.server_id) return
  
  uploadNodesLoading.value = true
  getPVEServerNodes(uploadForm.server_id).then(res => {
    const nodes = Array.isArray(res) ? res : res?.data || []
    uploadNodes.value = nodes.map(item => ({
      label: item.node || item.name,
      value: item.node || item.name
    }))
  }).catch(err => {
    Message.error('获取节点列表失败')
  }).finally(() => {
    uploadNodesLoading.value = false
  })
}

function handleUploadNodeChange() {
  uploadForm.storage = null
  uploadStorages.value = []
  
  if (!uploadForm.server_id || !uploadForm.node) return
  
  uploadStoragesLoading.value = true
  getNodeStorage(uploadForm.server_id, uploadForm.node).then(res => {
    const storages = Array.isArray(res) ? res : []
    // 只显示支持 ISO 或容器模板的存储
    uploadStorages.value = storages.filter(s => {
      const contentTypes = s.content?.split(',') || []
      return contentTypes.includes('iso') || contentTypes.includes('vztmpl')
    })
  }).catch(err => {
    Message.error('获取存储列表失败')
  }).finally(() => {
    uploadStoragesLoading.value = false
  })
}

function handleUpload() {
  if (!uploadForm.fileList.length) {
    Message.warning('请选择要上传的文件')
    return
  }
  
  const file = uploadForm.fileList[0].file
  if (!file) {
    Message.warning('文件无效')
    return
  }
  
  if (!uploadForm.server_id || !uploadForm.node || !uploadForm.storage) {
    Message.warning('请完整填写上传信息')
    return
  }
  
  const formData = new FormData()
  formData.append('file', file)
  formData.append('content', uploadForm.content_type)
  formData.append('filename', file.name)
  
  uploadStorageContent(
    uploadForm.server_id,
    uploadForm.node,
    uploadForm.storage,
    formData
  ).then(() => {
    Message.success('上传成功')
    uploadModalVisible.value = false
    resetUploadForm()
    loadTemplates()
  }).catch(err => {
    Message.error('上传失败: ' + (err.message || '未知错误'))
  })
}

function resetUploadForm() {
  uploadForm.server_id = null
  uploadForm.node = null
  uploadForm.storage = null
  uploadForm.content_type = 'iso'
  uploadForm.fileList = []
  uploadNodes.value = []
  uploadStorages.value = []
}

function formatContentType(content) {
  const typeMap = {
    'iso': 'ISO镜像',
    'vztmpl': '容器模板',
    'backup': '备份文件'
  }
  return typeMap[content] || content || '未知'
}

function getContentTypeColor(content) {
  const colorMap = {
    'iso': 'blue',
    'vztmpl': 'green',
    'backup': 'orange'
  }
  return colorMap[content] || 'gray'
}

function formatBytes(bytes) {
  if (!bytes && bytes !== 0) return '-'
  const units = ['B', 'KB', 'MB', 'GB', 'TB']
  let index = 0
  let num = Number(bytes)
  while (num >= 1024 && index < units.length - 1) {
    num /= 1024
    index++
  }
  return `${num.toFixed(num >= 10 || num < 1 ? 1 : 2)} ${units[index]}`
}

function formatTime(timestamp) {
  if (!timestamp) return '-'
  try {
    const date = new Date(timestamp * 1000)
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    })
  } catch {
    return timestamp
  }
}

onMounted(() => {
  loadServers()
  loadTemplates()
})
</script>

<style scoped>
.pve-templates {
  padding: 24px;
  background: var(--color-bg-1);
  min-height: 100%;
}

.toolbar {
  margin-bottom: 16px;
}

.toolbar-field {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.toolbar-field .label {
  font-size: 13px;
  color: var(--color-text-2);
  font-weight: 500;
}
</style>

