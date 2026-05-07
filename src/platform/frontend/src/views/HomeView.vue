<template>
  <div class="home">
    <el-card class="welcome-card">
      <template #header>
        <div class="card-header">
          <span>欢迎使用源代码加密平台</span>
        </div>
      </template>
      
      <p>本平台可以帮助您加密Python和Vue项目，保护您的源代码不被非法复制。</p>
      
      <el-divider />
      
      <h3>使用步骤：</h3>
      <el-steps :active="0" direction="vertical">
        <el-step title="采集指纹" description="获取本机CPU和GPU的唯一标识" />
        <el-step title="配置加密" description="选择源代码路径、输出路径和有效期" />
        <el-step title="执行加密" description="系统自动混淆代码并嵌入指纹校验" />
        <el-step title="分发项目" description="将加密后的项目部署到目标机器" />
      </el-steps>
      
      <el-divider />
      
      <div class="actions">
        <el-button type="primary" @click="$router.push('/fingerprint')">
          <el-icon><Cpu /></el-icon>
          开始采集指纹
        </el-button>
      </div>
    </el-card>
  </div>
</template>

<style scoped>
.home {
  max-width: 800px;
  margin: 0 auto;
}

.welcome-card {
  margin-top: 20px;
}

.card-header {
  font-size: 18px;
  font-weight: bold;
}

.actions {
  text-align: center;
  margin-top: 20px;
}
</style>
