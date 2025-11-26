<template>
  <div class="pve-storage">
    <a-card class="storage-card">
      <template #title>
        <div class="card-title">
          <a-typography-title :heading="4">PVE 存储管理</a-typography-title>
          <a-space>
            <a-button type="outline" size="small" @click="loadStorages" :disabled="!selectedServer || !selectedNode">
              刷新
            </a-button>
          </a-space>
        </div>
      </template>

      <div class="storage-toolbar">
        <a-space size="large" wrap>
          <div class="toolbar-field">
            <div class="label">服务器</div>
            <a-select
              v-model="selectedServer"
              placeholder="请选择PVE服务器"
              :loading="serversLoading"
              allow-clear
              style="min-width: 220px"
            >
              <a-option
                v-for="server in serverOptions"
                :key="server.value"
                :value="server.value"
              >
                {{ server.label }}
              </a-option>
            </a-select>
          </div>
          <div class="toolbar-field">
            <div class="label">节点</div>
            <a-select
              v-model="selectedNode"
              placeholder="请选择节点"
              :loading="nodesLoading"
              allow-clear
              style="min-width: 200px"
            >
              <a-option
                v-for="node in nodeOptions"
                :key="node.value"
                :value="node.value"
              >
                {{ node.label }}
              </a-option>
            </a-select>
          </div>
        </a-space>
      </div>

      <div class="storage-summary" v-if="storageList.length">
        <a-space size="large">
          <div class="summary-item">
            <div class="label">总容量</div>
            <div class="value">{{ formatBytes(summary.total) }}</div>
          </div>
          <div class="summary-item">
            <div class="label">已用</div>
            <div class="value">{{ formatBytes(summary.used) }}</div>
          </div>
          <div class="summary-item">
            <div class="label">可用</div>
            <div class="value">{{ formatBytes(summary.avail) }}</div>
          </div>
        </a-space>
      </div>

      <a-empty
        v-if="!storageList.length && !storageLoading"
        description="请选择服务器与节点后查看存储信息"
      />

      <a-table
        v-else
        :columns="columns"
        :data="storageList"
        :loading="storageLoading"
        :bordered="false"
        :pagination="false"
        row-key="storage"
        style="margin-top: 12px"
      >
        <template #content="{ record }">
          <a-space wrap>
            <a-tag v-for="item in record.__contentList" :key="item">{{ item }}</a-tag>
          </a-space>
        </template>
        <template #shared="{ record }">
          <a-tag :color="record.shared ? 'arcoblue' : 'gray'">
            {{ record.shared ? '是' : '否' }}
          </a-tag>
        </template>
        <template #enabled="{ record }">
          <a-tag :color="record.enabled ? 'green' : 'red'">
            {{ record.enabled ? '启用' : '禁用' }}
          </a-tag>
        </template>
        <template #usage="{ record }">
          <div class="usage-cell">
            <a-progress
              :percent="record.__usagePercent"
              :status="record.__usagePercent >= 90 ? 'danger' : record.__usagePercent >= 70 ? 'warning' : 'success'"
              :show-text="false"
            />
            <div class="usage-text">
              {{ formatBytes(record.__used) }} / {{ formatBytes(record.total) }} ({{ record.__usagePercent }}%)
            </div>
          </div>
        </template>
        <template #actions="{ record }">
          <a-space>
            <a-button type="text" size="small" @click="openContentDrawer(record)">查看内容</a-button>
          </a-space>
        </template>
      </a-table>
    </a-card>

    <a-drawer
      v-model:visible="contentDrawerVisible"
      :width="620"
      :mask-closable="false"
      title="存储内容"
    >
      <template v-if="currentStorage">
        <div class="drawer-header">
          <div>服务器：{{ currentServerName }}</div>
          <div>节点：{{ currentStorage.__node || selectedNode }}</div>
          <div>存储：{{ currentStorage.storage }}</div>
        </div>
        <div class="drawer-toolbar">
          <a-radio-group v-model="contentType" type="button" size="small">
            <a-radio
              v-for="item in drawerContentTypeOptions"
              :key="item.value"
              :value="item.value"
            >
              {{ item.label }}
            </a-radio>
          </a-radio-group>
          <a-upload
            v-if="contentType === 'iso'"
            :show-file-list="false"
            :custom-request="handleUpload"
            :disabled="uploading"
          >
            <a-button type="primary" size="small" :loading="uploading">
              上传 ISO
            </a-button>
          </a-upload>
        </div>
      </template>
      <a-spin :loading="contentLoading">
        <a-table
          v-if="contentList.length"
          :data="contentList"
          :pagination="false"
          :bordered="false"
          row-key="volid"
          size="small"
        >
          <template #columns>
            <a-table-column title="卷标" data-index="volid" />
            <a-table-column
              v-if="contentType === 'all'"
              title="类型"
              data-index="content"
            />
            <a-table-column title="大小" data-index="size">
              <template #cell="{ record }">
                {{ formatBytes(record.size) }}
              </template>
            </a-table-column>
            <a-table-column
              v-if="contentType !== 'iso'"
              title="格式"
              data-index="format"
            />
            <a-table-column
              v-if="contentType === 'images' || contentType === 'all'"
              title="VMID"
              data-index="vmid"
            />
            <a-table-column title="更新时间" data-index="ctime">
              <template #cell="{ record }">
                {{ formatTime(record.ctime) }}
              </template>
            </a-table-column>
          </template>
        </a-table>
        <a-empty v-else-if="!contentLoading" description="暂无内容" />
      </a-spin>
    </a-drawer>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted } from 'vue'
import dayjs from 'dayjs'
import { Message } from '@arco-design/web-vue'
import {
  getPVEServers,
  getPVEServerNodes,
  getNodeStorage,
  getStorageContent,
  uploadStorageContent
} from '@/api/pve'

const servers = ref([])
const serverOptions = computed(() =>
  servers.value.map(server => ({
    label: `${server.name} (${server.host})`,
    value: server.id
  }))
)
const nodes = ref([])
const ALL_NODES_VALUE = '__ALL_NODES__'
const nodeOptions = computed(() => {
  const options = nodes.value
    .map(node => ({
      label: node.node || node.name,
      value: node.node || node.name
    }))
    .filter(option => option.value)
  if (options.length) {
    return [{ label: '全部节点', value: ALL_NODES_VALUE }, ...options]
  }
  return options
})

const selectedServer = ref(null)
const selectedNode = ref('')

const serversLoading = ref(false)
const nodesLoading = ref(false)
const storageLoading = ref(false)
const contentLoading = ref(false)
const uploading = ref(false)

const storageList = ref([])
const contentList = ref([])
const contentDrawerVisible = ref(false)
const currentStorage = ref(null)
const contentType = ref('iso')
const contentTypeOptions = [
  { label: 'ISO 镜像', value: 'iso' },
  { label: '磁盘镜像', value: 'images' },
  { label: '模板', value: 'vztmpl' },
  { label: '备份', value: 'backup' },
  { label: '全部', value: 'all' }
]

const drawerContentTypeOptions = computed(() => {
  if (!currentStorage.value || !currentStorage.value.__contentList?.length) {
    return contentTypeOptions
  }
  const supported = new Set(currentStorage.value.__contentList)
  return contentTypeOptions.filter(
    (item) => item.value === 'all' || supported.has(item.value)
  )
})

const formatBytes = (bytes) => {
  if (bytes === null || bytes === undefined) return '-'
  if (bytes === 0) return '0 B'
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
  const i = Math.floor(Math.log(bytes) / Math.log(1024))
  const value = bytes / Math.pow(1024, i)
  return `${value.toFixed(value >= 10 || i === 0 ? 0 : 1)} ${sizes[i]}`
}

const formatTime = (timestamp) => {
  if (!timestamp) return '-'
  const date = dayjs(timestamp * 1000)
  return date.isValid() ? date.format('YYYY-MM-DD HH:mm') : '-'
}

const showNodeColumn = computed(() => selectedNode.value === ALL_NODES_VALUE)

const columns = computed(() => {
  const base = [
    { title: '存储', dataIndex: 'storage', width: 160 },
    { title: '类型', dataIndex: 'type', width: 120 },
    { title: '内容类型', slotName: 'content', width: 260 },
    { title: '共享', slotName: 'shared', width: 100 },
    { title: '状态', slotName: 'enabled', width: 100 },
    { title: '总容量', dataIndex: 'total', width: 140, render: ({ record }) => formatBytes(record.total) },
    { title: '可用', dataIndex: 'avail', width: 140, render: ({ record }) => formatBytes(record.avail) },
    { title: '使用情况', slotName: 'usage', width: 220 },
    { title: '操作', slotName: 'actions', width: 120, fixed: 'right' }
  ]
  if (showNodeColumn.value) {
    base.splice(1, 0, { title: '节点', dataIndex: '__node', width: 140 })
  }
  return base
})

const summary = computed(() => {
  const total = storageList.value.reduce((sum, item) => sum + (item.total || 0), 0)
  const avail = storageList.value.reduce((sum, item) => sum + (item.avail || 0), 0)
  const used = Math.max(total - avail, 0)
  return { total, avail, used }
})

const currentServerName = computed(() => {
  const server = servers.value.find(item => item.id === selectedServer.value)
  return server?.name || '-'
})

const enhanceStorageRecord = (record) => {
  const content = record.content
  let contentList = []
  if (typeof content === 'string') {
    contentList = content.split(',').map(item => item.trim()).filter(Boolean)
  } else if (Array.isArray(content)) {
    contentList = content
  }
  const total = Number(record.total) || 0
  const avail = Number(record.avail) || 0
  const used = total > 0 ? Math.max(total - avail, 0) : 0
  const usagePercent = total > 0 ? Math.min(100, Math.max(0, Number(((used / total) * 100).toFixed(1)))) : 0
  return {
    ...record,
    __contentList: contentList,
    __usagePercent: usagePercent,
    __used: used
  }
}

const resolveDefaultContentType = (record) => {
  const priority = ['iso', 'images', 'backup', 'vztmpl']
  const supported = record?.__contentList || []
  for (const type of priority) {
    if (supported.includes(type)) {
      return type
    }
  }
  return 'all'
}

const loadServers = async () => {
  serversLoading.value = true
  try {
    const res = await getPVEServers({ is_active: true, page_size: 100 })
    const list = Array.isArray(res) ? res : res?.results || []
    servers.value = list
    if (!selectedServer.value && list.length) {
      selectedServer.value = list[0].id
    }
  } catch (error) {
    Message.error('获取服务器列表失败：' + (error.message || '未知错误'))
  } finally {
    serversLoading.value = false
  }
}

const loadNodes = async () => {
  if (!selectedServer.value) {
    nodes.value = []
    selectedNode.value = ''
    storageList.value = []
    return
  }
  nodesLoading.value = true
  try {
    const res = await getPVEServerNodes(selectedServer.value)
    nodes.value = Array.isArray(res) ? res : res?.data || []
    if (!nodes.value.length) {
      selectedNode.value = ''
      storageList.value = []
      return
    }
    const firstNode = nodes.value[0].node || nodes.value[0].name
    const exists = nodes.value.some(node => (node.node || node.name) === selectedNode.value)
    if (!selectedNode.value || (!exists && selectedNode.value !== ALL_NODES_VALUE)) {
      selectedNode.value = firstNode
    }
  } catch (error) {
    Message.error('获取节点列表失败：' + (error.message || '未知错误'))
    nodes.value = []
    selectedNode.value = ''
    storageList.value = []
  } finally {
    nodesLoading.value = false
  }
}

const loadStorages = async () => {
  if (!selectedServer.value) {
    storageList.value = []
    return
  }
  const availableNodes = nodes.value
    .map(node => node.node || node.name)
    .filter(Boolean)
  let targetNodes = []
  if (selectedNode.value === ALL_NODES_VALUE) {
    targetNodes = availableNodes
  } else if (selectedNode.value) {
    targetNodes = [selectedNode.value]
  }
  if (!targetNodes.length) {
    storageList.value = []
    return
  }
  storageLoading.value = true
  const results = []
  try {
    for (const nodeName of targetNodes) {
      try {
        const res = await getNodeStorage(selectedServer.value, nodeName)
        const list = Array.isArray(res) ? res : []
        list.forEach(item => {
          results.push({
            ...enhanceStorageRecord(item),
            __node: nodeName
          })
        })
      } catch (error) {
        Message.error(`获取节点 ${nodeName} 存储失败：` + (error.message || '未知错误'))
      }
    }
    storageList.value = results
  } finally {
    storageLoading.value = false
  }
}

const loadContentList = async () => {
  if (!selectedServer.value || !selectedNode.value || !currentStorage.value) {
    contentList.value = []
    return
  }
  contentLoading.value = true
  try {
    const params = {}
    if (contentType.value && contentType.value !== 'all') {
      params.content = contentType.value
    }
    const nodeName = currentStorage.value.__node || selectedNode.value
    const res = await getStorageContent(
      selectedServer.value,
      nodeName,
      currentStorage.value.storage,
      params
    )
    contentList.value = Array.isArray(res) ? res : res?.data || []
  } catch (error) {
    contentList.value = []
    Message.error('获取存储内容失败：' + (error.message || '未知错误'))
  } finally {
    contentLoading.value = false
  }
}

const openContentDrawer = (record) => {
  currentStorage.value = record
  contentType.value = resolveDefaultContentType(record)
  contentDrawerVisible.value = true
  loadContentList()
}

const handleUpload = async (options) => {
  const { file, onSuccess, onError } = options
  if (!selectedServer.value || !selectedNode.value || !currentStorage.value) {
    onError?.(new Error('缺少目标存储信息'))
    return
  }
  uploading.value = true
  const formData = new FormData()
  formData.append('file', file)
  formData.append('filename', file.name)
  formData.append('content', 'iso')
  try {
    const nodeName = currentStorage.value.__node || selectedNode.value
    await uploadStorageContent(
      selectedServer.value,
      nodeName,
      currentStorage.value.storage,
      formData
    )
    Message.success('上传成功')
    onSuccess?.()
    loadContentList()
    loadStorages()
  } catch (error) {
    Message.error('上传失败：' + (error.message || '未知错误'))
    onError?.(error)
  } finally {
    uploading.value = false
  }
}

watch(selectedServer, (newVal, oldVal) => {
  if (newVal !== oldVal) {
    loadNodes()
  }
})

watch(selectedNode, (newVal, oldVal) => {
  if (newVal !== oldVal) {
    loadStorages()
  }
})

watch(contentType, (newVal, oldVal) => {
  if (newVal !== oldVal && contentDrawerVisible.value) {
    loadContentList()
  }
})

watch(contentDrawerVisible, (visible) => {
  if (!visible) {
    contentList.value = []
  } else if (visible && currentStorage.value) {
    loadContentList()
  }
})

onMounted(() => {
  loadServers()
})
</script>

<style scoped>
.pve-storage {
  padding: 16px;
}

.storage-card {
  width: 100%;
}

.card-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.storage-toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 24px;
  margin-bottom: 16px;
}

.toolbar-field {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.label {
  font-size: 12px;
  color: var(--color-text-3);
}

.storage-summary {
  margin-bottom: 12px;
}

.summary-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.summary-item .value {
  font-size: 18px;
  font-weight: 500;
}

.usage-cell {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.usage-text {
  font-size: 12px;
  color: var(--color-text-2);
}

.drawer-header {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-bottom: 12px;
  font-size: 13px;
  color: var(--color-text-2);
}

.drawer-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 12px;
}
</style>


