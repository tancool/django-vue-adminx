<template>
  <div class="pve-tasks">
    <a-card>
      <template #title>
        <a-typography-title :heading="4">全局任务中心</a-typography-title>
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
            <div class="label">状态</div>
            <a-select
              v-model="filters.statusfilter"
              placeholder="全部状态"
              style="width: 150px"
              @change="handleFilterChange"
            >
              <a-option value="all">全部状态</a-option>
              <a-option value="running">运行中</a-option>
              <a-option value="stopped">已停止</a-option>
            </a-select>
          </div>
          <a-button type="primary" @click="loadTasks" :loading="loading">
            <template #icon>
              <icon-refresh />
            </template>
            刷新
          </a-button>
        </a-space>
      </div>

      <!-- 任务表格 -->
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

        <template #type="{ record }">
          <a-tag :color="getTaskTypeColor(record.type)">
            {{ formatTaskType(record.type) }}
          </a-tag>
        </template>

        <template #status="{ record }">
          <a-tag :color="getStatusColor(record.status)">
            {{ formatStatus(record.status) }}
          </a-tag>
        </template>

        <template #time="{ record }">
          <div>
            <div>开始: {{ formatTime(record.starttime) }}</div>
            <div v-if="record.endtime" style="font-size: 12px; color: var(--color-text-3)">
              结束: {{ formatTime(record.endtime) }}
            </div>
            <div v-if="record.starttime && record.endtime" style="font-size: 12px; color: var(--color-text-3)">
              耗时: {{ formatDuration(record.endtime - record.starttime) }}
            </div>
          </div>
        </template>

        <template #actions="{ record }">
          <a-button type="text" size="small" @click="handleViewLog(record)">
            查看日志
          </a-button>
        </template>
      </a-table>
    </a-card>

    <!-- 任务日志对话框 -->
    <a-modal
      v-model:visible="logModalVisible"
      :title="`任务日志 - ${currentTask?.type || ''}`"
      width="800px"
      :footer="false"
    >
      <div class="log-container">
        <div class="log-header">
          <a-space>
            <span>服务器: {{ currentTask?.server_name }}</span>
            <span>节点: {{ currentTask?.node }}</span>
            <span>UPID: {{ currentTask?.upid }}</span>
          </a-space>
          <a-button size="small" @click="loadTaskLog" :loading="logLoading">
            <template #icon>
              <icon-refresh />
            </template>
            刷新日志
          </a-button>
        </div>
        <div class="log-content" ref="logContentRef">
          <pre v-if="taskLog.length">{{ taskLog.join('\n') }}</pre>
          <a-empty v-else description="暂无日志" />
        </div>
      </div>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { Message } from '@arco-design/web-vue'
import { IconRefresh } from '@arco-design/web-vue/es/icon'
import { getPVEServers, getGlobalTasks, getGlobalTaskLog } from '@/api/pve'

const loading = ref(false)
const logLoading = ref(false)
const servers = ref([])
const tableData = ref([])
const logModalVisible = ref(false)
const currentTask = ref(null)
const taskLog = ref([])
const logContentRef = ref(null)

const filters = reactive({
  server_id: null,
  node: '',
  statusfilter: 'all'
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
    title: '任务类型',
    dataIndex: 'type',
    slotName: 'type',
    width: 150
  },
  {
    title: '状态',
    dataIndex: 'status',
    slotName: 'status',
    width: 100
  },
  {
    title: '用户',
    dataIndex: 'user',
    width: 150
  },
  {
    title: '时间信息',
    dataIndex: 'time',
    slotName: 'time',
    width: 250
  },
  {
    title: '操作',
    slotName: 'actions',
    width: 100,
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

function loadTasks() {
  loading.value = true
  const params = {
    limit: pagination.pageSize * 2, // 获取更多数据用于前端分页
    ...filters
  }
  
  getGlobalTasks(params).then(res => {
    const result = res?.data || res || {}
    const tasks = result.tasks || []
    
    // 前端分页
    const start = (pagination.current - 1) * pagination.pageSize
    const end = start + pagination.pageSize
    tableData.value = tasks.slice(start, end)
    pagination.total = tasks.length
  }).catch(err => {
    Message.error('获取任务列表失败: ' + (err.message || '未知错误'))
    tableData.value = []
    pagination.total = 0
  }).finally(() => {
    loading.value = false
  })
}

function handleFilterChange() {
  pagination.current = 1
  loadTasks()
}

function handlePageChange(page) {
  pagination.current = page
  loadTasks()
}

function handlePageSizeChange(size) {
  pagination.pageSize = size
  pagination.current = 1
  loadTasks()
}

function handleViewLog(record) {
  currentTask.value = record
  logModalVisible.value = true
  taskLog.value = []
  loadTaskLog()
}

function loadTaskLog() {
  if (!currentTask.value) return
  
  logLoading.value = true
  getGlobalTaskLog({
    server_id: currentTask.value.server_id,
    node: currentTask.value.node,
    upid: currentTask.value.upid,
    start: 0,
    limit: 500
  }).then(res => {
    const result = res?.data || res || {}
    taskLog.value = result.log || []
    
    // 滚动到底部
    setTimeout(() => {
      if (logContentRef.value) {
        logContentRef.value.scrollTop = logContentRef.value.scrollHeight
      }
    }, 100)
  }).catch(err => {
    Message.error('获取任务日志失败: ' + (err.message || '未知错误'))
    taskLog.value = []
  }).finally(() => {
    logLoading.value = false
  })
}

function formatTaskType(type) {
  const typeMap = {
    'qmcreate': '创建虚拟机',
    'qmstart': '启动',
    'qmstop': '停止',
    'qmshutdown': '关机',
    'qmreboot': '重启',
    'qmrestore': '恢复',
    'vzdump': '备份',
    'qmsnapshot': '快照',
    'qmclone': '克隆',
    'qmconfig': '配置',
    'qmresize': '调整大小',
    'qmdelete': '删除'
  }
  return typeMap[type] || type || '未知'
}

function getTaskTypeColor(type) {
  const colorMap = {
    'qmcreate': 'blue',
    'qmstart': 'green',
    'qmstop': 'red',
    'qmshutdown': 'orange',
    'qmreboot': 'cyan',
    'qmrestore': 'purple',
    'vzdump': 'arcoblue',
    'qmsnapshot': 'pinkpurple',
    'qmclone': 'magenta',
    'qmconfig': 'gold',
    'qmresize': 'lime',
    'qmdelete': 'red'
  }
  return colorMap[type] || 'gray'
}

function formatStatus(status) {
  const statusMap = {
    'running': '运行中',
    'stopped': '已停止',
    'unknown': '未知'
  }
  return statusMap[status] || status || '未知'
}

function getStatusColor(status) {
  if (status === 'running') return 'green'
  if (status === 'stopped') return 'gray'
  return 'orange'
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

function formatDuration(seconds) {
  if (!seconds || seconds < 0) return '-'
  const sec = Math.floor(seconds)
  if (sec < 60) return `${sec}秒`
  if (sec < 3600) return `${Math.floor(sec / 60)}分${sec % 60}秒`
  const hours = Math.floor(sec / 3600)
  const minutes = Math.floor((sec % 3600) / 60)
  const secs = sec % 60
  return `${hours}小时${minutes}分${secs}秒`
}

onMounted(() => {
  loadServers()
  loadTasks()
})
</script>

<style scoped>
.pve-tasks {
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

.log-container {
  display: flex;
  flex-direction: column;
  height: 500px;
}

.log-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background: var(--color-bg-2);
  border-radius: 4px;
  margin-bottom: 12px;
}

.log-content {
  flex: 1;
  overflow-y: auto;
  background: #1e1e1e;
  color: #d4d4d4;
  padding: 16px;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 12px;
  line-height: 1.6;
}

.log-content pre {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-all;
}
</style>

