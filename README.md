# 文本总结助手

这是一个Windows桌面应用程序，可以帮助用户快速总结选中的文本内容。

## 功能特点

- 选中文本后自动检测
- 使用DeepSeek API进行智能文本总结
- 系统托盘常驻运行
- 简洁的浮动窗口界面

## 安装步骤

1. 确保已安装Python 3.8或更高版本
2. 安装依赖包：
   ```
   pip install -r requirements.txt
   ```
3. 在项目根目录创建`.env`文件，添加您的DeepSeek API密钥：
   ```
   DEEPSEEK_API_KEY=your_api_key_here
   ```
4. 运行图标生成脚本：
   ```
   python create_icon.py
   ```

## 使用方法

1. 运行应用程序：
   ```
   python text_summary_assistant.py
   ```
2. 程序会在系统托盘中显示图标
3. 在任何应用程序中选中文本
4. 程序会自动检测选中的文本并显示总结结果
5. 点击关闭按钮可以关闭总结窗口
6. 右键点击系统托盘图标可以退出程序

## 注意事项

- 需要有效的DeepSeek API密钥
- 确保网络连接正常
- 程序会每秒检查一次选中的文本，对系统资源影响较小

## 系统要求

- Windows 10 或更高版本
- Python 3.8+
- 网络连接 