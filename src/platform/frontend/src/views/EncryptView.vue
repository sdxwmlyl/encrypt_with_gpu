<template>
  <div class="encrypt-view">
    <h2>项目加密配置</h2>
    <p class="description">配置源代码路径、输出路径和有效期，开始加密项目</p>
    
    <el-card class="encrypt-card">
      <template #header>
        <div class="card-header">
          <span>加密配置</span>
        </div>
      </template>
      
      <el-form :model="form" label-width="120px" class="encrypt-form">
        <el-form-item label="源代码路径">
          <el-input
            v-model="form.sourcePath"
            placeholder="请输入源代码文件夹路径"
          >
            <template #append>
              <el-button @click="selectSourcePath">
                <el-icon><Folder /></el-icon>
                选择
              </el-button>
            </template>
          </el-input>
        </el-form-item>
        
        <el-form-item label="输出路径">
          <el-input
            v-model="form.outputPath"
            placeholder="请输入加密后项目输出路径"
          >
            <template #append>
              <el-button @click="selectOutputPath">
                <el-icon><Folder /></el-icon>
                选择
              </el-button>
            </template>
          </el-input>
        </el-form-item>
        
        <el-form-item label="有效期至">
          <el-date-picker
            v-model="form.expiryDate"
            type="date"
            placeholder="选择有效期截止日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            :disabled-date="disabledDate"
          />
        </el-form-item>
        
        <el-form-item label="设备指纹">
          <el-input
            v-model="form.fingerprint"
            type="textarea"
            :rows="2"
            placeholder="留空则使用本机指纹"
          />
        </el-form-item>
        
        <el-form-item>
          <el-button
            type="primary"
            size="large"
            @click="startEncrypt"
            :loading="encrypting"
            :disabled="!canEncrypt"
          >
            <el-icon><Lock /></el-icon>
            开始加密
          </el-button>
        </el-form-item>
      </el-form>
      
      <!-- 加密进度 -->
      <div v-if="status.status !== 'idle'" class="progress-section">
        <el-divider />
        <h4>加密进度</h4>
        <el-progress
          :percentage="status.progress"
          :status="status.status === 'completed' ? 'success' : status.status === 'error' ? 'exception' : ''"
        />
        <p class="status-message">{{ status.message }}</p>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const form = ref({
  sourcePath: '',
  outputPath: '',
  expiryDate: '',
  fingerprint: ''
})

const encrypting = ref(false)
const status = ref({
  status: 'idle',
  progress: 0,
  message: ''
})

let statusTimer = null

const canEncrypt = computed(() => {
  return form.value.sourcePath && 
         form.value.outputPath && 
         form.value.expiryDate &&
         !encrypting.value
})

const disabledDate = (time) => {
  return time.getTime() < Date.now()
}

const selectSourcePath = () => {
  // 实际应用中这里会打开文件选择对话框
  const path = prompt('请输入源代码路径:')
  if (path) form.value.sourcePath = path
}

const selectOutputPath = () => {
  const path = prompt('请输入输出路径:')
  if (path) form.value.outputPath = path
}

const startEncrypt = async () => {
  encrypting.value = true
  try {
    const response = await axios.post('/api/encrypt', {
      source_path: form.value.sourcePath,
      output_path: form.value.outputPath,
      expiry_date: form.value.expiryDate,
      fingerprint: form.value.fingerprint || undefined
    })
    
    if (response.data.success) {
      ElMessage.success('加密任务已启动')
      startStatusPolling()
    }
  } catch (error) {
    ElMessage.error('启动加密失败: ' + (error.response?.data?.detail || error.message))
    encrypting.value = false
  }
}

const startStatusPolling = () => {
  statusTimer = setInterval(async () => {
    try {
      const response = await axios.get('/api/encrypt/status')
      status.value = response.data
      
      if (status.value.status === 'completed' || status.value.status === 'error') {
        encrypting.value = false
        clearInterval(statusTimer)
        
        if (status.value.status === 'completed') {
          ElMessage.success('加密完成！')
        }
      }
    } catch (error) {
      console.error('获取状态失败:', error)
    }
  }, 1000)
}

const fetchFingerprint = async () => {
  try {
    const response = await axios.get('/api/fingerprint')
    if (response.data.success) {
      form.value.fingerprint = response.data.data.combined_hash
    }
  } catch (error) {
    console.error('获取指纹失败:', error)
  }
}

onMounted(() => {
  fetchFingerprint()
})

onUnmounted(() => {
  if (statusTimer) clearInterval(statusTimer)
})
</script>

<style scoped>
.encrypt-view {
  max-width: 800px;
  margin: 0 auto;
}

.description {
  color: #666;
  margin-bottom: 20px;
}

.encrypt-card {
  margin-top: 20px;
}

.encrypt-form {
  max-width: 600px;
}

.progress-section {
  margin-top: 30px;
}

.status-message {
  text-align: center;
  color: #666;
  margin-top: 10px;
}
</style>
