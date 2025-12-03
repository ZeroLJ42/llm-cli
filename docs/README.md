# LLM CLI

终端 LLM 交互工具，支持多 session、流式、文件输入、Markdown 渲染和 Rich UI。

## 快速开始

```bash
# 1. 虚拟环境 & 依赖
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. 配置
cp .env.example .env
nano .env  # 填 API key

# 3. 运行
python3 main.py
```

## 功能

- **Rich UI** - 漂亮的终端界面，支持 Markdown 渲染、表格和面板
- **流式输出** - 默认启用，实时显示 AI 回复
- **文件输入** - `@file.txt` 读取文件，`@` 用默认文件
- **多 session** - `/session` 管理独立对话 (新建、切换、删除、重命名)
- **动态配置** - `/config` 在运行时修改 API Key、URL 和模型
- **自动保存** - `/exit` 自动保存历史

## 命令

```
/help              帮助
/history           查看历史
/stats             统计信息
/clear             清空历史
/system <msg>      设置系统提示
/stream            切换流式模式
/session           管理 sessions (list/switch/new/delete/rename)
/config            配置 API 客户端
/exit              退出并保存
```

## 输入

```
@file.txt          从 file.txt 读取
@                  从默认文件读取 (input.txt)
普通文本           直接发送
```

## 项目结构

```
main.py            CLI 应用 (Rich + prompt_toolkit)
core/
  chat_manager.py  对话管理
  api_client.py    API 客户端
config/
  config.py        配置
docs/              文档
```
