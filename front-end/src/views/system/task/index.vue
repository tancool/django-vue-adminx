<template>
  <div class="task-page">
    <a-card>
      <template #title>
        <a-typography-title :heading="5">任务管理</a-typography-title>
      </template>
      <div class="toolbar" style="margin-bottom:12px;">
        <a-space>
          <a-button type="primary" @click="openEdit()">新增</a-button>
          <a-input v-model="query.name" placeholder="按名称搜索" allow-clear style="width:200px" />
          <a-select v-model="query.trigger_type" allow-clear placeholder="触发类型" style="width:140px">
            <a-option value="cron">Cron</a-option>
            <a-option value="interval">Interval</a-option>
            <a-option value="date">Once</a-option>
          </a-select>
          <a-button @click="fetchList">查询</a-button>
        </a-space>
      </div>
      <a-table :data="list" :loading="loading" row-key="id">
        <a-table-column title="名称" data-index="name" />
        <a-table-column title="触发类型" data-index="trigger_type" />
        <a-table-column title="函数" data-index="func_path" />
        <a-table-column title="启用" :render="({record}) => record.enabled ? '是' : '否'" />
        <a-table-column title="最近执行" data-index="last_run_at" />
        <a-table-column title="操作" :width="220"
                        :render="({record}) => renderActions(record)" />
      </a-table>
    </a-card>

    <a-modal v-model:visible="visible" :title="form.id ? '编辑任务' : '新增任务'" @ok="submit" :mask-closable="false">
      <a-form :model="form" layout="vertical">
        <a-form-item field="name" label="名称" required>
          <a-input v-model="form.name" />
        </a-form-item>
        <a-form-item field="func_path" label="函数路径" required>
          <a-input v-model="form.func_path" placeholder="apps.tasks.examples:demo_task" />
        </a-form-item>
        <a-form-item field="trigger_type" label="触发类型" required>
          <a-select v-model="form.trigger_type">
            <a-option value="cron">Cron</a-option>
            <a-option value="interval">Interval</a-option>
            <a-option value="date">Once</a-option>
          </a-select>
        </a-form-item>
        <template v-if="form.trigger_type==='cron'">
          <a-form-item label="Cron 秒">
            <a-input v-model="form.cron_second" />
          </a-form-item>
          <a-form-item label="Cron 分">
            <a-input v-model="form.cron_minute" />
          </a-form-item>
          <a-form-item label="Cron 时">
            <a-input v-model="form.cron_hour" />
          </a-form-item>
          <a-form-item label="Cron 日">
            <a-input v-model="form.cron_day" />
          </a-form-item>
          <a-form-item label="Cron 月">
            <a-input v-model="form.cron_month" />
          </a-form-item>
          <a-form-item label="Cron 周">
            <a-input v-model="form.cron_day_of_week" />
          </a-form-item>
        </template>
        <template v-else-if="form.trigger_type==='interval'">
          <a-form-item label="间隔(秒)" required>
            <a-input-number v-model="form.interval_seconds" :min="1" />
          </a-form-item>
        </template>
        <template v-else>
          <a-form-item label="一次性时间">
            <a-date-picker v-model="form.once_run_at" show-time style="width:100%" />
          </a-form-item>
        </template>
        <a-form-item label="Args(JSON 数组)">
          <a-input v-model="argsStr" placeholder='如 ["a", 1]' />
        </a-form-item>
        <a-form-item label="Kwargs(JSON 对象)">
          <a-input v-model="kwargsStr" placeholder='如 {"key": "v"}' />
        </a-form-item>
        <a-form-item label="启用">
          <a-switch v-model="form.enabled" />
        </a-form-item>
        <a-form-item label="描述">
          <a-textarea v-model="form.description" />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
  
</template>

<script setup>
import {ref, reactive, h} from 'vue'
import { Message, Modal } from '@arco-design/web-vue'
import { listTasks, createTask, updateTask, deleteTask, runTaskNow } from '@/api/task'

const loading = ref(false)
const list = ref([])
const visible = ref(false)
const form = reactive({ enabled: true, trigger_type: 'cron' })
const argsStr = ref('[]')
const kwargsStr = ref('{}')
const query = reactive({ name: '', trigger_type: undefined })

function fetchList() {
  loading.value = true
  listTasks(query).then(res => {
    list.value = res?.results || res || []
  }).finally(() => loading.value = false)
}

function openEdit(record) {
  Object.assign(form, { id: undefined, name: '', func_path: '', trigger_type: 'cron', cron_second: '0', cron_minute: '*', cron_hour: '*', cron_day: '*', cron_month: '*', cron_day_of_week: '*', interval_seconds: 60, once_run_at: undefined, enabled: true, description: '' })
  argsStr.value = '[]'
  kwargsStr.value = '{}'
  if (record) {
    Object.assign(form, record)
    argsStr.value = JSON.stringify(record.args || [])
    kwargsStr.value = JSON.stringify(record.kwargs || {})
  }
  visible.value = true
}

function submit() {
  try {
    form.args = JSON.parse(argsStr.value || '[]')
    form.kwargs = JSON.parse(kwargsStr.value || '{}')
  } catch (e) {
    Message.error('Args/Kwargs 需为合法 JSON')
    return
  }
  const api = form.id ? updateTask.bind(null, form.id) : createTask
  api(form).then(() => {
    Message.success('保存成功')
    visible.value = false
    fetchList()
  })
}

function handleDelete(record) {
  Modal.confirm({ title: '确认删除', content: `删除任务「${record.name}」?`, onOk: () => deleteTask(record.id).then(() => { Message.success('已删除'); fetchList() }) })
}

function handleRun(record) {
  runTaskNow(record.id).then(() => Message.success('已触发执行'))
}

function renderActions(record) {
  return [
    h('a-button', { type: 'text', onClick: () => openEdit(record) }, { default: () => '编辑' }),
    h('a-button', { type: 'text', onClick: () => handleRun(record) }, { default: () => '执行一次' }),
    h('a-button', { type: 'text', status: 'danger', onClick: () => handleDelete(record) }, { default: () => '删除' })
  ]
}

fetchList()
</script>

<style scoped>
.task-page { padding: 12px; }
</style>


