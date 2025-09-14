<template>
  <div v-if="show" class="error-message" :class="type">
    <div class="error-content">
      <div class="error-icon">
        <svg v-if="type === 'error'" viewBox="0 0 24 24" fill="currentColor">
          <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
        </svg>
        <svg v-else-if="type === 'warning'" viewBox="0 0 24 24" fill="currentColor">
          <path d="M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z"/>
        </svg>
        <svg v-else viewBox="0 0 24 24" fill="currentColor">
          <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z"/>
        </svg>
      </div>
      <div class="error-text">
        <h4 v-if="title" class="error-title">{{ title }}</h4>
        <p class="error-description">{{ message }}</p>
        <div v-if="details" class="error-details">
          <button @click="showDetails = !showDetails" class="details-toggle">
            {{ showDetails ? '隐藏详情' : '显示详情' }}
          </button>
          <pre v-if="showDetails" class="details-content">{{ details }}</pre>
        </div>
      </div>
      <button v-if="closable" @click="close" class="close-button">
        <svg viewBox="0 0 24 24" fill="currentColor">
          <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
        </svg>
      </button>
    </div>
    <div v-if="actions && actions.length" class="error-actions">
      <button 
        v-for="action in actions" 
        :key="action.label"
        @click="action.handler"
        :class="['action-button', action.type || 'default']"
      >
        {{ action.label }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

interface Action {
  label: string
  handler: () => void
  type?: 'primary' | 'secondary' | 'danger'
}

interface Props {
  show?: boolean
  type?: 'error' | 'warning' | 'info'
  title?: string
  message: string
  details?: string
  closable?: boolean
  actions?: Action[]
}

const props = withDefaults(defineProps<Props>(), {
  show: true,
  type: 'error',
  closable: true
})

const emit = defineEmits<{
  close: []
}>()

const showDetails = ref(false)

const close = () => {
  emit('close')
}
</script>

<style scoped>
.error-message {
  border-radius: 8px;
  padding: 16px;
  margin: 16px 0;
  border-left: 4px solid;
}

.error-message.error {
  background-color: #fef2f2;
  border-left-color: #ef4444;
  color: #dc2626;
}

.error-message.warning {
  background-color: #fffbeb;
  border-left-color: #f59e0b;
  color: #d97706;
}

.error-message.info {
  background-color: #eff6ff;
  border-left-color: #3b82f6;
  color: #2563eb;
}

.error-content {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.error-icon {
  flex-shrink: 0;
  width: 20px;
  height: 20px;
  margin-top: 2px;
}

.error-icon svg {
  width: 100%;
  height: 100%;
}

.error-text {
  flex: 1;
}

.error-title {
  margin: 0 0 4px 0;
  font-size: 16px;
  font-weight: 600;
}

.error-description {
  margin: 0;
  font-size: 14px;
  line-height: 1.5;
}

.error-details {
  margin-top: 8px;
}

.details-toggle {
  background: none;
  border: none;
  color: currentColor;
  text-decoration: underline;
  cursor: pointer;
  font-size: 12px;
  padding: 0;
}

.details-content {
  margin-top: 8px;
  padding: 8px;
  background-color: rgba(0, 0, 0, 0.05);
  border-radius: 4px;
  font-size: 12px;
  overflow-x: auto;
  white-space: pre-wrap;
}

.close-button {
  flex-shrink: 0;
  background: none;
  border: none;
  color: currentColor;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-button:hover {
  background-color: rgba(0, 0, 0, 0.1);
}

.error-actions {
  margin-top: 12px;
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.action-button {
  padding: 6px 12px;
  border-radius: 4px;
  border: 1px solid;
  cursor: pointer;
  font-size: 12px;
  font-weight: 500;
  transition: all 0.2s;
}

.action-button.primary {
  background-color: currentColor;
  color: white;
  border-color: currentColor;
}

.action-button.secondary {
  background-color: transparent;
  color: currentColor;
  border-color: currentColor;
}

.action-button.danger {
  background-color: #ef4444;
  color: white;
  border-color: #ef4444;
}

.action-button.default {
  background-color: transparent;
  color: currentColor;
  border-color: currentColor;
}

.action-button:hover {
  opacity: 0.8;
}
</style>