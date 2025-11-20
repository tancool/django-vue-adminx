<template>
  <div class="document-page">
    <a-card>
      <template #title>
        <a-typography-title :heading="5">在线文档</a-typography-title>
      </template>

      <div class="toolbar">
        <a-space>
          <a-button type="primary" @click="handleCreate">
            <template #icon>
              <icon-plus />
            </template>
            新建文档
          </a-button>
          <a-input-search
            v-model="searchText"
            placeholder="搜索标题或内容"
            style="width: 260px"
            @search="fetchList"
            @clear="fetchList"
            allow-clear
          />
        </a-space>
      </div>

      <a-table
        :data="tableData"
        :loading="loading"
        row-key="id"
        :pagination="pagination"
        @page-change="handlePageChange"
        @page-size-change="handlePageSizeChange"
        :bordered="false"
        :hoverable="true"
      >
        <template #columns>
          <a-table-column title="标题" data-index="title" />
          <a-table-column title="置顶" data-index="is_pinned">
            <template #cell="{ record }">
              <a-tag :color="record.is_pinned ? 'gold' : 'blue'">
                {{ record.is_pinned ? '已置顶' : '普通' }}
              </a-tag>
            </template>
          </a-table-column>
          <a-table-column title="更新时间" data-index="updated_at">
            <template #cell="{ record }">
              {{ formatDate(record.updated_at) }}
            </template>
          </a-table-column>
          <a-table-column title="创建人" data-index="created_by">
            <template #cell="{ record }">
              {{ record.created_by?.username || '-' }}
            </template>
          </a-table-column>
          <a-table-column title="操作" :width="220">
            <template #cell="{ record }">
              <a-space :size="8">
                <a-button type="text" size="small" @click="handleEdit(record)">编辑</a-button>
                <a-button type="text" size="small" @click="handleTogglePin(record)">
                  {{ record.is_pinned ? '取消置顶' : '置顶' }}
                </a-button>
                <a-button type="text" size="small" status="danger" @click="handleDelete(record)">
                  删除
                </a-button>
              </a-space>
            </template>
          </a-table-column>
        </template>
      </a-table>
    </a-card>

    <a-modal
      v-model:visible="editorVisible"
      :title="currentId ? '编辑文档' : '新建文档'"
      :fullscreen="true"
      :footer="false"
    >
      <div class="editor-wrapper">
        <a-space direction="vertical" style="width: 100%">
          <a-input
            v-model="form.title"
            placeholder="请输入文档标题"
            allow-clear
            size="large"
          />
          <!-- wangEditor 工具栏 -->
          <Toolbar
            style="border-bottom: 1px solid #e5e6eb"
            :editor="editorRef"
            :defaultConfig="toolbarConfig"
            mode="default"
          />
          <!-- wangEditor 编辑器 -->
          <Editor
            v-model="form.content"
            style="height: 480px; overflow-y: hidden; border: 1px solid #e5e6eb"
            :defaultConfig="editorConfig"
            mode="default"
            @onCreated="handleEditorCreated"
          />
          <div class="editor-footer">
            <a-space>
              <a-switch v-model="form.is_pinned" />
              <span>置顶</span>
            </a-space>
            <a-space style="margin-left: auto">
              <a-button @click="editorVisible = false">关闭</a-button>
              <a-button type="primary" :loading="saving" @click="handleSave">
                保存
              </a-button>
            </a-space>
          </div>
        </a-space>
      </div>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onBeforeUnmount, shallowRef } from 'vue'
import { Message, Modal } from '@arco-design/web-vue'
import { IconPlus } from '@arco-design/web-vue/es/icon'
import '@wangeditor/editor/dist/css/style.css'
import { Editor, Toolbar } from '@wangeditor/editor-for-vue'
import {
  getDocumentList,
  getDocumentDetail,
  createDocument,
  updateDocument,
  deleteDocument,
  togglePinDocument,
} from '@/api/office'

const loading = ref(false)
const tableData = ref([])
const searchText = ref('')

const pagination = reactive({
  current: 1,
  pageSize: 10,
  total: 0,
  showTotal: true,
  showPageSize: true,
})

const editorVisible = ref(false)
const saving = ref(false)
const currentId = ref(null)

// wangEditor 相关
const editorRef = shallowRef(null)
const toolbarConfig = {}
const editorConfig = {
  placeholder: '在这里输入文档内容...',
}

const form = reactive({
  title: '',
  content: '',
  is_pinned: false,
})

function handleEditorCreated(editor) {
  editorRef.value = editor
}

function formatDate(value) {
  if (!value) return '-'
  try {
    const d = new Date(value)
    if (Number.isNaN(d.getTime())) return value
    return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(
      d.getDate(),
    ).padStart(2, '0')} ${String(d.getHours()).padStart(2, '0')}:${String(
      d.getMinutes(),
    ).padStart(2, '0')}:${String(d.getSeconds()).padStart(2, '0')}`
  } catch (e) {
    return value
  }
}

async function fetchList() {
  loading.value = true
  try {
    const params = {
      page: pagination.current,
      page_size: pagination.pageSize,
    }
    if (searchText.value) {
      params.search = searchText.value
    }
    const res = await getDocumentList(params)
    const data = res
    if (Array.isArray(data.results)) {
      tableData.value = data.results
      pagination.total = data.count || data.results.length
    } else if (Array.isArray(data)) {
      tableData.value = data
      pagination.total = data.length
    } else {
      tableData.value = []
      pagination.total = 0
    }
  } catch (e) {
    Message.error('获取文档列表失败：' + (e.message || '未知错误'))
  } finally {
    loading.value = false
  }
}

function handlePageChange(page) {
  pagination.current = page
  fetchList()
}

function handlePageSizeChange(size) {
  pagination.pageSize = size
  pagination.current = 1
  fetchList()
}

function resetForm() {
  form.title = ''
  form.content = ''
  form.is_pinned = false
  currentId.value = null
}

function handleCreate() {
  resetForm()
  editorVisible.value = true
}

async function handleEdit(record) {
  try {
    const res = await getDocumentDetail(record.id)
    const data = res
    currentId.value = data.id
    form.title = data.title || ''
    form.content = data.content || ''
    form.is_pinned = !!data.is_pinned
    editorVisible.value = true
  } catch (e) {
    Message.error('获取文档详情失败：' + (e.message || '未知错误'))
  }
}

async function handleSave() {
  if (!form.title) {
    Message.warning('请输入标题')
    return
  }
  saving.value = true
  try {
    const payload = {
      title: form.title,
      content: form.content,
      is_pinned: form.is_pinned,
    }
    if (currentId.value) {
      await updateDocument(currentId.value, payload)
      Message.success('更新成功')
    } else {
      await createDocument(payload)
      Message.success('创建成功')
    }
    editorVisible.value = false
    fetchList()
  } catch (e) {
    Message.error('保存失败：' + (e.message || '未知错误'))
  } finally {
    saving.value = false
  }
}

function handleDelete(record) {
  Modal.confirm({
    title: '确认删除',
    content: `确定要删除文档「${record.title}」吗？`,
    onOk: async () => {
      try {
        await deleteDocument(record.id)
        Message.success('删除成功')
        fetchList()
      } catch (e) {
        Message.error('删除失败：' + (e.message || '未知错误'))
      }
    },
  })
}

async function handleTogglePin(record) {
  try {
    await togglePinDocument(record.id)
    Message.success(record.is_pinned ? '已取消置顶' : '已置顶')
    fetchList()
  } catch (e) {
    Message.error('操作失败：' + (e.message || '未知错误'))
  }
}

onMounted(() => {
  fetchList()
})

onBeforeUnmount(() => {
  const editor = editorRef.value
  if (editor == null) return
  editor.destroy()
})
</script>

<style scoped>
.document-page {
  padding: 20px;
}

.toolbar {
  margin-bottom: 12px;
}

.editor-wrapper {
  padding: 12px 0;
}

.editor-footer {
  display: flex;
  align-items: center;
  margin-top: 12px;
}
</style>


