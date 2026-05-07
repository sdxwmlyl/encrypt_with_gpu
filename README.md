# 源代码加密系统

一个跨平台（Linux/Windows）本地运行的源代码加密系统，用于保护Python和Vue项目不被非法复制。

## 功能特性

- 🔐 **单向加密**：代码混淆后无法逆向还原
- 🖥️ **指纹绑定**：绑定CPU+GPU硬件指纹，防止非法迁移
- ⏰ **有效期控制**：可设置项目使用截止日期
- 🌐 **跨平台**：支持Linux和Windows系统
- 📦 **离线运行**：加密后的项目无需联网验证
- 🖥️ **Web界面**：提供友好的图形化操作界面

## 项目结构

```
projects/encryption-system/
├── src/
│   ├── fingerprint/          # 指纹采集模块
│   │   ├── collector.py      # 统一采集器
│   │   ├── cpu_linux.py      # Linux CPU采集
│   │   ├── gpu_linux.py      # Linux GPU采集
│   │   ├── cpu_windows.py    # Windows CPU采集
│   │   └── gpu_windows.py    # Windows GPU采集
│   ├── encryptor/            # 加密引擎
│   │   ├── python_obfuscator.py  # Python代码混淆
│   │   └── fp_binding.py     # 指纹绑定代码生成
│   └── platform/             # 加密平台
│       ├── backend/          # FastAPI后端
│       │   ├── main.py
│       │   └── requirements.txt
│       └── frontend/         # Vue前端
│           ├── src/views/    # 页面组件
│           ├── package.json
│           └── vite.config.js
├── test-project/             # 测试项目
│   ├── backend/              # Python后端测试
│   └── frontend/             # Vue前端测试
└── test_encryption.py        # 闭环测试脚本
```

## 快速开始

### Linux/macOS

#### 1. 安装依赖

```bash
# 后端依赖
cd src/platform/backend
pip install -r requirements.txt

# 前端依赖
cd ../frontend
npm install
```

#### 2. 启动加密平台

**方式一：使用启动脚本（推荐）**
```bash
./start.sh
```

**方式二：手动启动**
```bash
# 启动后端（终端1）
cd src/platform/backend
python main.py

# 启动前端（终端2）
cd src/platform/frontend
npm run dev
```

### Windows

#### 1. 安装依赖

```cmd
:: 后端依赖
cd src\platform\backend
pip install -r requirements.txt

:: 前端依赖
cd ..\frontend
npm install
```

#### 2. 启动加密平台

**方式一：使用启动脚本（推荐）**
```cmd
start.bat
```

**方式二：手动启动**
```cmd
:: 启动后端（命令行窗口1）
cd src\platform\backend
python main.py

:: 启动前端（命令行窗口2）
cd src\platform\frontend
npm run dev
```

### 3. 使用加密平台

1. 打开浏览器访问 `http://localhost:5173`
2. 进入"指纹采集"页面获取本机指纹
3. 进入"项目加密"页面配置加密参数
4. 点击"开始加密"完成加密

### 4. 运行测试

```bash
# 运行闭环测试
python test_encryption.py
```

## 加密流程

1. **采集指纹**：获取本机CPU和GPU的唯一标识
2. **配置加密**：设置源代码路径、输出路径和有效期
3. **代码混淆**：使用AST解析和变量名替换混淆代码
4. **指纹绑定**：在代码中嵌入指纹校验和有效期检查
5. **生成项目**：输出加密后的项目文件

## 安全机制

### 指纹校验
- 运行时自动采集当前设备指纹
- 与加密时绑定的指纹进行比对
- 不匹配则抛出异常并终止运行

### 有效期控制
- 硬编码有效期到加密代码中
- 运行时检查当前日期是否超过有效期
- 过期后项目无法启动

### 代码混淆
- 变量名、函数名替换为随机字符串
- 保留Python语法结构，确保功能正常
- 增加逆向分析难度

## 异常测试

系统包含以下异常测试：

1. **过期测试**：修改系统时间验证过期后项目无法运行
2. **指纹不匹配测试**：在其他设备上运行验证指纹校验
3. **破解测试**：尝试逆向分析加密后的代码

## 技术栈

- **后端**：Python 3.10+, FastAPI
- **前端**：Vue 3, Element Plus
- **加密**：AST解析, 代码混淆
- **指纹采集**：系统指令 (Linux: lspci, Windows: wmic)

## 跨平台支持

| 功能 | Linux | Windows |
|------|-------|---------|
| CPU指纹采集 | ✅ `/proc/cpuinfo` | ✅ `wmic cpu` |
| GPU指纹采集 | ✅ `lspci` | ✅ `wmic path win32_VideoController` |
| Python加密 | ✅ | ✅ |
| Vue加密 | ✅ | ✅ |
| Web平台 | ✅ | ✅ |
| 启动脚本 | `start.sh` | `start.bat` |

## 注意事项

1. 加密后的项目只能在绑定指纹的设备上运行
2. 请妥善保管加密前的源代码
3. 有效期设置后无法修改，请合理规划
4. 建议在加密前备份原始项目

## 许可证

本项目仅供学习和研究使用。
