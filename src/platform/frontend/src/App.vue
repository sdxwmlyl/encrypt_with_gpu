<template>
  <div class="app">
    <el-container>
      <el-header class="header">
        <h1>
          <el-icon><Lock /></el-icon>
          源代码加密平台
        </h1>
      </el-header>
      <el-container>
        <el-aside width="200px" class="sidebar">
          <el-menu
            :default-active="$route.path"
            router
            class="menu"
          >
            <el-menu-item index="/">
              <el-icon><HomeFilled /></el-icon>
              <span>首页</span>
            </el-menu-item>
            <el-menu-item index="/fingerprint">
              <el-icon><Cpu /></el-icon>
              <span>指纹采集</span>
            </el-menu-item>
            <el-menu-item index="/encrypt">
              <el-icon><Lock /></el-icon>
              <span>项目加密</span>
            </el-menu-item>
          </el-menu>
        </el-aside>
        <el-main class="main">
          <router-view />
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<style scoped>
.app {
  height: 100vh;
}

.header {
  background: #409eff;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
}

.header h1 {
  margin: 0;
  font-size: 20px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.sidebar {
  background: #f5f7fa;
}

.menu {
  height: 100%;
  border-right: none;
}

.main {
  padding: 20px;
  background: #fff;
}
</style>
