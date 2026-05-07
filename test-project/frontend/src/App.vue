<template>
  <div class="app">
    <h1>Hello from Test Project</h1>
    <p>这是一个用于测试加密系统的示例项目</p>
    
    <div class="actions">
      <button @click="callBackend" :disabled="loading">
        {{ loading ? '调用中...' : '调用后端API' }}
      </button>
    </div>
    
    <div v-if="response" class="response">
      <h3>后端响应:</h3>
      <pre>{{ JSON.stringify(response, null, 2) }}</pre>
    </div>
    
    <div v-if="error" class="error">
      <h3>错误:</h3>
      <p>{{ error }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const loading = ref(false)
const response = ref(null)
const error = ref(null)

const callBackend = async () => {
  loading.value = true
  error.value = null
  response.value = null
  
  try {
    const res = await fetch('/api/hello')
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    response.value = await res.json()
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}
</script>

<style>
.app {
  max-width: 600px;
  margin: 50px auto;
  padding: 20px;
  font-family: Arial, sans-serif;
}

h1 {
  color: #333;
}

.actions {
  margin: 20px 0;
}

button {
  padding: 10px 20px;
  font-size: 16px;
  cursor: pointer;
  background: #409eff;
  color: white;
  border: none;
  border-radius: 4px;
}

button:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.response, .error {
  margin-top: 20px;
  padding: 15px;
  border-radius: 4px;
}

.response {
  background: #f0f9eb;
  border: 1px solid #67c23a;
}

.error {
  background: #fef0f0;
  border: 1px solid #f56c6c;
}

pre {
  background: #f5f5f5;
  padding: 10px;
  border-radius: 4px;
  overflow-x: auto;
}
</style>
