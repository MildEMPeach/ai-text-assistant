# AI 文本总结与翻译助手

![应用图标](icon.png)

这是一个功能强大的Windows桌面应用程序，可以帮助用户快速总结和翻译选中的文本内容。

## ✨ 功能特点

- 🔍 **智能文本检测**：选中文本后自动检测，无需手动操作
- 📊 **AI 文本总结**：使用 DeepSeek API 进行智能文本总结
- 🌐 **多语言翻译**：支持翻译到12种常用语言
- 🎨 **现代化界面**：深色主题，流畅动画，用户体验优秀
- ⚡ **实时流式响应**：边生成边显示，响应迅速
- 🔧 **灵活配置**：可自定义 API 设置和目标语言
- 💾 **系统托盘**：常驻运行，不占用桌面空间
- 🎯 **智能监控**：采用智能轮询机制，资源占用极低
- 👆 **便捷操作**：左键选择功能，右键隐藏图标

## 🚀 安装步骤

### 1. 环境准备
确保已安装 Python 3.8 或更高版本

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 配置 API
在项目根目录创建 `.env` 文件，添加您的 DeepSeek API 配置：
```env
DEEPSEEK_API_KEY=your_api_key_here
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
TARGET_LANGUAGE=中文
```



## 📖 使用方法

### 启动应用
```bash
# 直接运行
python text_summary_assistant.py

# 或使用批处理文件（推荐）
run_assistant.bat

# 静默运行（无控制台窗口）
run_assistant_silent.vbs
```

### 基本操作
1. **启动程序**：程序会在系统托盘中显示图标
2. **选中文本**：在任何应用程序中选中需要处理的文本
3. **等待图标出现**：程序会自动检测到文本选择并显示浮动图标
4. **选择操作**：左键点击浮动图标，选择：
   - 📊 **AI 总结**：生成文本摘要
   - 🌐 **翻译文本**：翻译到目标语言
5. **查看结果**：在浮动窗口中实时查看处理结果
6. **复制内容**：点击复制按钮将结果复制到剪贴板
7. **隐藏图标**：右键点击浮动图标可手动隐藏

### 图标操作说明
- **左键点击**：显示操作菜单（总结/翻译）
- **右键点击**：隐藏浮动图标
- **自动隐藏**：选择操作后图标会自动消失

### 系统托盘菜单
- **设置**：配置 API 密钥和翻译语言
- **关于**：查看应用信息和使用说明
- **退出**：关闭应用程序

## 🌍 支持的翻译语言

- 中文 (Chinese)
- English (英语)
- 日本語 (Japanese)
- 한국어 (Korean)
- Español (Spanish)
- Français (French)
- Deutsch (German)
- Русский (Russian)
- Português (Portuguese)
- Italiano (Italian)
- Nederlands (Dutch)
- Polski (Polish)

## ⚙️ 高级配置

### 环境变量说明
```env
# DeepSeek API 密钥（必需）
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxx

# API 基础地址（可选，默认为官方地址）
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1

# 默认翻译目标语言（可选，默认为中文）
TARGET_LANGUAGE=English
```

### 文件结构
```
ai-text-assistant/
├── text_summary_assistant.py  # 主程序文件
├── requirements.txt           # 依赖包列表
├── .env                      # 环境配置文件
├── icon.png                  # 应用图标
├── run_assistant.bat         # Windows 批处理启动文件
├── run_assistant_silent.vbs  # 静默启动脚本
└── README.md                 # 说明文档
```

## 🔧 技术特性

- **智能监控算法**：根据鼠标活动智能调整检测频率
- **线程安全设计**：多线程处理，界面响应流畅
- **流式 API 调用**：支持实时显示生成过程
- **剪贴板保护**：自动恢复原剪贴板内容
- **DPI 自适应**：支持高分辨率显示器
- **内存优化**：智能资源管理，长期运行稳定
- **稳定显示**：浮动图标稳定显示，不会意外消失

## 📋 系统要求

- **操作系统**：Windows 10 或更高版本
- **Python 版本**：3.8+
- **网络连接**：需要访问 DeepSeek API
- **内存要求**：至少 100MB 可用内存
- **磁盘空间**：约 50MB

## 🐛 故障排除

### 常见问题

**Q: 程序无法启动，出现 "ImportError: DLL load failed while importing QtCore" 错误？**
A: 这是PyQt6版本兼容性问题，请按以下步骤解决：
1. 完全卸载现有PyQt6：`pip uninstall PyQt6 PyQt6-Qt6 PyQt6-sip -y`
2. 重新安装兼容版本：`pip install PyQt6==6.4.2 PyQt6-Qt6==6.4.2 PyQt6-sip==13.4.0`
3. 如果仍有问题，请安装 [Visual C++ Redistributable](https://aka.ms/vs/17/release/vc_redist.x64.exe)
4. 详细解决方案请查看 [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

**Q: 程序无法启动？**
A: 检查 Python 版本（推荐3.8-3.11）和依赖包是否正确安装

**Q: 无法检测到选中的文本？**
A: 确保文本已正确选中，程序会自动检测并显示图标

**Q: 图标出现后立即消失？**
A: 这个问题已经修复，图标现在会稳定显示直到您点击或右键隐藏

**Q: 出现 "Client.init() got an unexpected keyword argument 'proxies'" 错误？**
A: 这是 openai 库与 httpx 库版本兼容性问题。**已修复**！解决方法：
1. **推荐方案**：重新安装依赖 `pip install -r requirements.txt --force-reinstall`
2. **手动修复**：`pip install openai==1.55.3 httpx==0.27.2 --force-reinstall`
3. 如果在 Google Colab 中，安装后需要重启运行时
4. 这个问题在 openai 1.55.3+ 版本中已经完全解决

**Q: API 调用失败？**
A: 检查网络连接和 API 密钥配置

**Q: 翻译结果不准确？**
A: 可以在设置中调整目标语言，或重新选择文本

### 详细故障排除
如果遇到PyQt6相关问题，请查看详细的 [故障排除指南](TROUBLESHOOTING.md)

### 日志查看
程序运行时会在控制台输出详细日志，有助于问题诊断。

## 📄 许可证

本项目采用 MIT 许可证，详见 LICENSE 文件。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request 来改进这个项目！

## 📞 支持

如果您在使用过程中遇到问题，请：
1. 查看本文档的故障排除部分
2. 检查控制台输出的错误信息
3. 提交 Issue 描述具体问题

---

**Powered by DeepSeek API** 🚀

## 🤖 项目说明

这个项目是由 AI 助手生成的代码实现，但创意和想法来自 **MildEMPeach** 😄

虽然代码是 AI 写的，但每一个功能需求、用户体验优化和设计决策都源于人类的创造力和洞察力。这是人工智能与人类创意完美结合的典型例子！

*"AI 负责编码，人类负责创意"* ✨ 