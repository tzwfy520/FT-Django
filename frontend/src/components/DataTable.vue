<template>
  <div class="data-table">
    <!-- 表格工具栏 -->
    <div v-if="showToolbar" class="table-toolbar">
      <div class="toolbar-left">
        <slot name="toolbar-left">
          <input 
            v-if="searchable"
            v-model="searchQuery"
            type="text"
            placeholder="搜索..."
            class="search-input"
          />
        </slot>
      </div>
      <div class="toolbar-right">
        <slot name="toolbar-right">
          <button v-if="refreshable" @click="refresh" class="refresh-button">
            <svg viewBox="0 0 24 24" fill="currentColor">
              <path d="M17.65 6.35C16.2 4.9 14.21 4 12 4c-4.42 0-7.99 3.58-7.99 8s3.57 8 7.99 8c3.73 0 6.84-2.55 7.73-6h-2.08c-.82 2.33-3.04 4-5.65 4-3.31 0-6-2.69-6-6s2.69-6 6-6c1.66 0 3.14.69 4.22 1.78L13 11h7V4l-2.35 2.35z"/>
            </svg>
            刷新
          </button>
        </slot>
      </div>
    </div>

    <!-- 表格容器 -->
    <div class="table-container" :class="{ 'loading': loading }">
      <table class="table">
        <thead>
          <tr>
            <th 
              v-for="column in columns" 
              :key="column.key"
              :class="[
                'table-header',
                { 'sortable': column.sortable },
                { 'sorted': sortBy === column.key }
              ]"
              :style="{ width: column.width }"
              @click="column.sortable && sort(column.key)"
            >
              <div class="header-content">
                <span>{{ column.title }}</span>
                <div v-if="column.sortable" class="sort-icons">
                  <svg 
                    :class="{ 'active': sortBy === column.key && sortOrder === 'asc' }"
                    viewBox="0 0 24 24" 
                    fill="currentColor"
                  >
                    <path d="M7 14l5-5 5 5z"/>
                  </svg>
                  <svg 
                    :class="{ 'active': sortBy === column.key && sortOrder === 'desc' }"
                    viewBox="0 0 24 24" 
                    fill="currentColor"
                  >
                    <path d="M7 10l5 5 5-5z"/>
                  </svg>
                </div>
              </div>
            </th>
            <th v-if="hasActions" class="table-header actions-header">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loading" class="loading-row">
            <td :colspan="columns.length + (hasActions ? 1 : 0)" class="loading-cell">
              <Loading message="加载数据中..." />
            </td>
          </tr>
          <tr v-else-if="filteredData.length === 0" class="empty-row">
            <td :colspan="columns.length + (hasActions ? 1 : 0)" class="empty-cell">
              <div class="empty-content">
                <svg viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
                </svg>
                <p>{{ emptyText }}</p>
              </div>
            </td>
          </tr>
          <tr 
            v-else
            v-for="(item, index) in paginatedData" 
            :key="getRowKey(item, index)"
            class="table-row"
            :class="{ 'selected': selectedRows.includes(getRowKey(item, index)) }"
            @click="rowClickable && handleRowClick(item, index)"
          >
            <td 
              v-for="column in columns" 
              :key="column.key"
              class="table-cell"
              :class="column.align ? `text-${column.align}` : ''"
            >
              <slot 
                :name="`cell-${column.key}`" 
                :item="item" 
                :value="getColumnValue(item, column.key)"
                :index="index"
              >
                <span v-if="column.render" v-html="column.render(getColumnValue(item, column.key), item, index)"></span>
                <span v-else>{{ formatValue(getColumnValue(item, column.key), column.format) }}</span>
              </slot>
            </td>
            <td v-if="hasActions" class="table-cell actions-cell">
              <slot name="actions" :item="item" :index="index">
                <div class="action-buttons">
                  <button 
                    v-for="action in actions" 
                    :key="action.key"
                    @click.stop="action.handler(item, index)"
                    :class="['action-button', action.type || 'default']"
                    :disabled="action.disabled && action.disabled(item)"
                    :title="action.title"
                  >
                    <svg v-if="action.icon" viewBox="0 0 24 24" fill="currentColor">
                      <path :d="action.icon"/>
                    </svg>
                    <span v-if="action.label">{{ action.label }}</span>
                  </button>
                </div>
              </slot>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 分页器 -->
    <div v-if="pageable && filteredData.length > pageSize" class="pagination">
      <div class="pagination-info">
        显示 {{ (currentPage - 1) * pageSize + 1 }} - {{ Math.min(currentPage * pageSize, filteredData.length) }} 条，
        共 {{ filteredData.length }} 条
      </div>
      <div class="pagination-controls">
        <button 
          @click="currentPage = 1" 
          :disabled="currentPage === 1"
          class="page-button"
        >
          首页
        </button>
        <button 
          @click="currentPage--" 
          :disabled="currentPage === 1"
          class="page-button"
        >
          上一页
        </button>
        <span class="page-info">{{ currentPage }} / {{ totalPages }}</span>
        <button 
          @click="currentPage++" 
          :disabled="currentPage === totalPages"
          class="page-button"
        >
          下一页
        </button>
        <button 
          @click="currentPage = totalPages" 
          :disabled="currentPage === totalPages"
          class="page-button"
        >
          末页
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import Loading from './Loading.vue'

interface Column {
  key: string
  title: string
  width?: string
  sortable?: boolean
  align?: 'left' | 'center' | 'right'
  format?: string
  render?: (value: any, item: any, index: number) => string
}

interface Action {
  key: string
  label?: string
  icon?: string
  type?: 'primary' | 'secondary' | 'danger' | 'default'
  title?: string
  handler: (item: any, index: number) => void
  disabled?: (item: any) => boolean
}

interface Props {
  data: any[]
  columns: Column[]
  actions?: Action[]
  loading?: boolean
  searchable?: boolean
  sortable?: boolean
  pageable?: boolean
  pageSize?: number
  rowKey?: string | ((item: any, index: number) => string | number)
  rowClickable?: boolean
  showToolbar?: boolean
  refreshable?: boolean
  emptyText?: string
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
  searchable: true,
  sortable: true,
  pageable: true,
  pageSize: 20,
  rowKey: 'id',
  rowClickable: false,
  showToolbar: true,
  refreshable: true,
  emptyText: '暂无数据'
})

const emit = defineEmits<{
  refresh: []
  rowClick: [item: any, index: number]
  selectionChange: [selectedRows: (string | number)[]]
}>()

const searchQuery = ref('')
const sortBy = ref('')
const sortOrder = ref<'asc' | 'desc'>('asc')
const currentPage = ref(1)
const selectedRows = ref<(string | number)[]>([])

const hasActions = computed(() => props.actions && props.actions.length > 0)

const filteredData = computed(() => {
  let result = [...props.data]
  
  // 搜索过滤
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(item => 
      props.columns.some(column => {
        const value = getColumnValue(item, column.key)
        return String(value).toLowerCase().includes(query)
      })
    )
  }
  
  // 排序
  if (sortBy.value) {
    result.sort((a, b) => {
      const aValue = getColumnValue(a, sortBy.value)
      const bValue = getColumnValue(b, sortBy.value)
      
      let comparison = 0
      if (aValue < bValue) comparison = -1
      else if (aValue > bValue) comparison = 1
      
      return sortOrder.value === 'desc' ? -comparison : comparison
    })
  }
  
  return result
})

const totalPages = computed(() => Math.ceil(filteredData.value.length / props.pageSize))

const paginatedData = computed(() => {
  if (!props.pageable) return filteredData.value
  
  const start = (currentPage.value - 1) * props.pageSize
  const end = start + props.pageSize
  return filteredData.value.slice(start, end)
})

const getRowKey = (item: any, index: number): string | number => {
  if (typeof props.rowKey === 'function') {
    return props.rowKey(item, index)
  }
  return item[props.rowKey] || index
}

const getColumnValue = (item: any, key: string) => {
  return key.split('.').reduce((obj, k) => obj?.[k], item)
}

const formatValue = (value: any, format?: string) => {
  if (value == null) return '-'
  
  if (format === 'currency') {
    return `¥${Number(value).toFixed(2)}`
  } else if (format === 'percent') {
    return `${(Number(value) * 100).toFixed(2)}%`
  } else if (format === 'date') {
    return new Date(value).toLocaleDateString()
  } else if (format === 'datetime') {
    return new Date(value).toLocaleString()
  }
  
  return value
}

const sort = (key: string) => {
  if (sortBy.value === key) {
    sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortBy.value = key
    sortOrder.value = 'asc'
  }
}

const refresh = () => {
  emit('refresh')
}

const handleRowClick = (item: any, index: number) => {
  emit('rowClick', item, index)
}

// 重置分页当搜索条件改变时
watch(searchQuery, () => {
  currentPage.value = 1
})
</script>

<style scoped>
.data-table {
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.table-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid #e5e7eb;
  background-color: #f9fafb;
}

.search-input {
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
  width: 200px;
}

.refresh-button {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
}

.refresh-button svg {
  width: 16px;
  height: 16px;
}

.table-container {
  overflow-x: auto;
}

.table {
  width: 100%;
  border-collapse: collapse;
}

.table-header {
  background-color: #f9fafb;
  padding: 12px;
  text-align: left;
  font-weight: 600;
  color: #374151;
  border-bottom: 1px solid #e5e7eb;
  white-space: nowrap;
}

.table-header.sortable {
  cursor: pointer;
  user-select: none;
}

.table-header.sortable:hover {
  background-color: #f3f4f6;
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.sort-icons {
  display: flex;
  flex-direction: column;
  margin-left: 8px;
}

.sort-icons svg {
  width: 12px;
  height: 12px;
  color: #9ca3af;
}

.sort-icons svg.active {
  color: #3b82f6;
}

.table-row {
  border-bottom: 1px solid #e5e7eb;
}

.table-row:hover {
  background-color: #f9fafb;
}

.table-row.selected {
  background-color: #eff6ff;
}

.table-cell {
  padding: 12px;
  color: #374151;
  vertical-align: middle;
}

.text-center {
  text-align: center;
}

.text-right {
  text-align: right;
}

.actions-cell {
  width: 120px;
}

.action-buttons {
  display: flex;
  gap: 4px;
}

.action-button {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 8px;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  background: white;
  color: #374151;
  cursor: pointer;
  font-size: 12px;
}

.action-button:hover:not(:disabled) {
  background-color: #f3f4f6;
}

.action-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.action-button.primary {
  background: #3b82f6;
  color: white;
  border-color: #3b82f6;
}

.action-button.danger {
  background: #ef4444;
  color: white;
  border-color: #ef4444;
}

.action-button svg {
  width: 14px;
  height: 14px;
}

.loading-cell,
.empty-cell {
  padding: 40px;
  text-align: center;
}

.empty-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  color: #9ca3af;
}

.empty-content svg {
  width: 48px;
  height: 48px;
}

.pagination {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-top: 1px solid #e5e7eb;
  background-color: #f9fafb;
}

.pagination-info {
  font-size: 14px;
  color: #6b7280;
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: 8px;
}

.page-button {
  padding: 6px 12px;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  background: white;
  color: #374151;
  cursor: pointer;
  font-size: 14px;
}

.page-button:hover:not(:disabled) {
  background-color: #f3f4f6;
}

.page-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  font-size: 14px;
  color: #6b7280;
  margin: 0 8px;
}
</style>