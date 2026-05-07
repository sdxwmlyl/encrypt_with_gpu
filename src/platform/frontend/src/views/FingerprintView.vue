<template>
  <div class="fingerprint-view">
    <h2>设备指纹采集</h2>
    <p class="description">采集本机的CPU和GPU指纹，用于绑定加密项目</p>
    
    <el-card class="fingerprint-card">
      <template #header>
        <div class="card-header">
          <span>本机指纹信息</span>
          <el-button type="primary" @click="collectFingerprint" :loading="loading">
            <el-icon><Refresh /></el-icon>
            重新采集
          </el-button>
        </div>
      </template>
      
      <div v-if="fingerprint" class="fingerprint-info">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="操作系统">
            {{ fingerprint.platform.system }} {{ fingerprint.platform.release }}
          </el-descriptions-item>
          <el-descriptions-item label="CPU ID">
            <el-tag type="success">{{ fingerprint.cpu.id }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="GPU ID">
            <el-tag type="warning">{{ fingerprint.gpu.id }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="组合指纹哈希">
            <el-input
              v-model="fingerprint.combined_hash"
              readonly
              class="hash-input"
            >
              <template #append>
                <el-button @click="copyHash">
                  <el-icon><CopyDocument /></el-icon>
                </el-button>
              </template>
            </el-input>
          </el-descriptions-item>
        </el-descriptions>
        
        <el-divider />
        
        <div class="actions">
          <el-button type="success" @click="$router.push('/encrypt')">
            <el-icon><ArrowRight /></el-icon>
            下一步：配置加密
          </el-button>
        </div>
      </div>
      
      <el-empty v-else description="点击上方按钮采集指纹" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const fingerprint = ref(null)
const loading = ref(false)

const collectFingerprint = async () => {
  loading.value = true
  try {
    const response = await axios.get('/api/fingerprint')
    if (response.data.success) {
      fingerprint.value = response.data.data
      ElMessage.success('指纹采集成功')
    }
  } catch (error) {
    ElMessage.error('指纹采集失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    loading.value = false
  }
}

const copyHash = () => {
  navigator.clipboard.writeText(fingerprint.value.combined_hash)
  ElMessage.success('已复制到剪贴板')
}

onMounted(() => {
  collectFingerprint()
})
</script>

<style scoped>
.fingerprint-view {
  max-width: 800px;
  margin: 0 auto;
}

.description {
  color: #666;
  margin-bottom: 20px;
}

.fingerprint-card {
  margin-top: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.fingerprint-info {
  padding: 20px 0;
}

.hash-input {
  width: 100%;
}

.actions {
  text-align: center;
  margin-top: 20px;
}
</style>
