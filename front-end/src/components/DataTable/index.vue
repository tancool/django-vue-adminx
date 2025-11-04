<template>
  <div class="data-table">
    <a-table
      :columns="columns"
      :data="data"
      :loading="loading"
      :pagination="pagination"
      @page-change="handlePageChange"
      @page-size-change="handlePageSizeChange"
      :bordered="false"
      :hoverable="true"
    >
      <template #actions="{ record }">
        <a-button type="text" size="small" @click="handleEdit(record)">编辑</a-button>
        <a-button type="text" size="small" status="danger" @click="handleDelete(record)">删除</a-button>
      </template>
    </a-table>
  </div>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue'

const props = defineProps({
  columns: {
    type: Array,
    required: true
  },
  data: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  },
  pagination: {
    type: Object,
    default: () => ({
      current: 1,
      pageSize: 20,
      total: 0,
      showTotal: true,
      showPageSize: true
    })
  }
})

const emit = defineEmits(['edit', 'delete', 'page-change', 'page-size-change'])

const handleEdit = (record) => {
  emit('edit', record)
}

const handleDelete = (record) => {
  emit('delete', record)
}

const handlePageChange = (page) => {
  emit('page-change', page)
}

const handlePageSizeChange = (pageSize) => {
  emit('page-size-change', pageSize)
}
</script>

<style scoped>
.data-table {
  padding: 20px;
}
</style>

