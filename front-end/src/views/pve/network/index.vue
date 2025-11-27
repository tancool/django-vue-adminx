<template>
  <div class="pve-network">
    <a-card>
      <template #title>
        <a-typography-title :heading="4">网络管理</a-typography-title>
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
            <div class="label">类型</div>
            <a-select
              v-model="filters.type"
              placeholder="全部类型"
              style="width: 150px"
              @change="handleFilterChange"
            >
              <a-option value="all">全部类型</a-option>
              <a-option value="bridge">桥接</a-option>
              <a-option value="bond">绑定</a-option>
              <a-option value="eth">以太网</a-option>
              <a-option value="vlan">VLAN</a-option>
            </a-select>
          </div>
          <a-button type="primary" @click="loadNetworks" :loading="loading">
            <template #icon>
              <icon-refresh />
            </template>
            刷新
          </a-button>
        </a-space>
      </div>

      <!-- 网络接口表格 -->
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
          <a-tag :color="getTypeColor(record.type)">
            {{ formatType(record.type) }}
          </a-tag>
        </template>

        <template #addresses="{ record }">
          <div v-if="record.addresses && record.addresses.length">
            <div
              v-for="(addr, idx) in record.addresses"
              :key="idx"
              style="margin-bottom: 4px"
            >
              <a-tag size="small" :color="addr.family === 'inet' ? 'blue' : 'green'">
                {{ addr.address }}/{{ addr.netmask || addr.prefix }}
              </a-tag>
            </div>
          </div>
          <span v-else style="color: var(--color-text-3)">-</span>
        </template>

        <template #status="{ record }">
          <a-tag :color="record.active ? 'green' : 'gray'">
            {{ record.active ? '活动' : '未激活' }}
          </a-tag>
        </template>

        <template #details="{ record }">
          <a-space direction="vertical" size="small" style="font-size: 12px">
            <div v-if="record.bridge">
              <span style="color: var(--color-text-3)">桥接:</span>
              <span style="margin-left: 4px">{{ record.bridge }}</span>
            </div>
            <div v-if="record.slaves">
              <span style="color: var(--color-text-3)">从属:</span>
              <span style="margin-left: 4px">{{ record.slaves }}</span>
            </div>
            <div v-if="record.vlan_raw_device">
              <span style="color: var(--color-text-3)">VLAN设备:</span>
              <span style="margin-left: 4px">{{ record.vlan_raw_device }}</span>
            </div>
            <div v-if="record.method">
              <span style="color: var(--color-text-3)">方法:</span>
              <span style="margin-left: 4px">{{ record.method }}</span>
            </div>
          </a-space>
        </template>

        <template #actions="{ record }">
          <a-button type="text" size="small" @click="handleViewDetails(record)">
            详情
          </a-button>
        </template>
      </a-table>
    </a-card>

    <!-- 详情对话框 -->
    <a-modal
      v-model:visible="detailModalVisible"
      :title="`网络接口详情 - ${currentNetwork?.iface || ''}`"
      width="700px"
      :footer="false"
    >
      <a-descriptions
        v-if="currentNetwork"
        :column="2"
        bordered
      >
        <a-descriptions-item label="服务器">
          {{ currentNetwork.server_name }}
        </a-descriptions-item>
        <a-descriptions-item label="节点">
          {{ currentNetwork.node }}
        </a-descriptions-item>
        <a-descriptions-item label="接口名称">
          {{ currentNetwork.iface }}
        </a-descriptions-item>
        <a-descriptions-item label="类型">
          <a-tag :color="getTypeColor(currentNetwork.type)">
            {{ formatType(currentNetwork.type) }}
          </a-tag>
        </a-descriptions-item>
        <a-descriptions-item label="状态">
          <a-tag :color="currentNetwork.active ? 'green' : 'gray'">
            {{ currentNetwork.active ? '活动' : '未激活' }}
          </a-tag>
        </a-descriptions-item>
        <a-descriptions-item label="自动启动">
          <a-tag :color="currentNetwork.autostart ? 'blue' : 'gray'">
            {{ currentNetwork.autostart ? '是' : '否' }}
          </a-tag>
        </a-descriptions-item>
        <a-descriptions-item
          v-if="currentNetwork.addresses && currentNetwork.addresses.length"
          label="IP地址"
          :span="2"
        >
          <div style="display: flex; flex-wrap: wrap; gap: 8px">
            <a-tag
              v-for="(addr, idx) in currentNetwork.addresses"
              :key="idx"
              :color="addr.family === 'inet' ? 'blue' : 'green'"
            >
              {{ addr.address }}/{{ addr.netmask || addr.prefix }}
              <span style="margin-left: 4px; opacity: 0.7">
                ({{ addr.family === 'inet' ? 'IPv4' : 'IPv6' }})
              </span>
            </a-tag>
          </div>
        </a-descriptions-item>
        <a-descriptions-item
          v-if="currentNetwork.method"
          label="配置方法"
        >
          {{ currentNetwork.method }}
        </a-descriptions-item>
        <a-descriptions-item
          v-if="currentNetwork.gateway"
          label="网关"
        >
          {{ currentNetwork.gateway }}
        </a-descriptions-item>
        <a-descriptions-item
          v-if="currentNetwork.bridge"
          label="桥接"
        >
          {{ currentNetwork.bridge }}
        </a-descriptions-item>
        <a-descriptions-item
          v-if="currentNetwork.slaves"
          label="从属接口"
        >
          {{ currentNetwork.slaves }}
        </a-descriptions-item>
        <a-descriptions-item
          v-if="currentNetwork.vlan_raw_device"
          label="VLAN原始设备"
        >
          {{ currentNetwork.vlan_raw_device }}
        </a-descriptions-item>
        <a-descriptions-item
          v-if="currentNetwork.bond_mode"
          label="绑定模式"
        >
          {{ currentNetwork.bond_mode }}
        </a-descriptions-item>
        <a-descriptions-item
          v-if="currentNetwork.mtu"
          label="MTU"
        >
          {{ currentNetwork.mtu }}
        </a-descriptions-item>
        <a-descriptions-item
          v-if="currentNetwork.comments"
          label="备注"
          :span="2"
        >
          {{ currentNetwork.comments }}
        </a-descriptions-item>
      </a-descriptions>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { Message } from '@arco-design/web-vue'
import { IconRefresh } from '@arco-design/web-vue/es/icon'
import { getPVEServers, getPVEServerNodes, getNodeNetwork } from '@/api/pve'

const loading = ref(false)
const servers = ref([])
const tableData = ref([])
const detailModalVisible = ref(false)
const currentNetwork = ref(null)

const filters = reactive({
  server_id: null,
  node: '',
  type: 'all'
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
    title: '接口名称',
    dataIndex: 'iface',
    width: 150
  },
  {
    title: '类型',
    dataIndex: 'type',
    slotName: 'type',
    width: 120
  },
  {
    title: 'IP地址',
    dataIndex: 'addresses',
    slotName: 'addresses',
    width: 200
  },
  {
    title: '状态',
    dataIndex: 'status',
    slotName: 'status',
    width: 100
  },
  {
    title: '详细信息',
    dataIndex: 'details',
    slotName: 'details',
    width: 200
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

async function loadNetworks() {
  loading.value = true
  const allNetworks = []
  
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
          // 获取网络接口列表
          const networksRes = await getNodeNetwork(server.id, nodeName)
          const networks = Array.isArray(networksRes) ? networksRes : []
          
          for (const network of networks) {
            // 类型筛选
            if (filters.type !== 'all' && network.type !== filters.type) {
              continue
            }
            
            allNetworks.push({
              ...network,
              server_id: server.id,
              server_name: server.name,
              server_host: server.host,
              node: nodeName
            })
          }
        } catch (err) {
          console.warn(`获取节点 ${nodeName} 网络失败:`, err)
        }
      }
    } catch (err) {
      console.warn(`获取服务器 ${server.name} 节点失败:`, err)
    }
  }
  
  // 前端分页
  const start = (pagination.current - 1) * pagination.pageSize
  const end = start + pagination.pageSize
  tableData.value = allNetworks.slice(start, end)
  pagination.total = allNetworks.length
  
  loading.value = false
}

function handleFilterChange() {
  pagination.current = 1
  loadNetworks()
}

function handlePageChange(page) {
  pagination.current = page
  loadNetworks()
}

function handlePageSizeChange(size) {
  pagination.pageSize = size
  pagination.current = 1
  loadNetworks()
}

function handleViewDetails(record) {
  currentNetwork.value = record
  detailModalVisible.value = true
}

function formatType(type) {
  const typeMap = {
    'bridge': '桥接',
    'bond': '绑定',
    'eth': '以太网',
    'vlan': 'VLAN',
    'alias': '别名',
    'OVSBridge': 'OVS桥接',
    'OVSBond': 'OVS绑定',
    'OVSIntPort': 'OVS内部端口'
  }
  return typeMap[type] || type || '未知'
}

function getTypeColor(type) {
  const colorMap = {
    'bridge': 'blue',
    'bond': 'green',
    'eth': 'cyan',
    'vlan': 'orange',
    'alias': 'purple',
    'OVSBridge': 'arcoblue',
    'OVSBond': 'pinkpurple',
    'OVSIntPort': 'magenta'
  }
  return colorMap[type] || 'gray'
}

onMounted(() => {
  loadServers()
  loadNetworks()
})
</script>

<style scoped>
.pve-network {
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

