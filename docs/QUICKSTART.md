# 快速开始

## 安装 (1分钟)

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 配置 (1分钟)

```bash
cp .env.example .env
nano .env  # 填入 API key
```

## 测试

```bash
python3 test_config.py
```

## 运行

```bash
python3 main.py
```

## 常见用法

启用流式 (已默认开启):
```
/stream
```

从文件读取:
```
@test_input.txt    # 显示内容后确认
@                  # 用默认文件 input.txt
```

多 session 管理:
```
/session           # 列出所有
/session new s1    # 创建新 session
/session switch s1 # 切换 session
```

从历史继续:
```
/continue          # 选择位置开始新对话
```

查看帮助:
```
/help
```

## 示例代码

以下是一个简单的代码示例，展示如何调用 LLM API：

```python
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ.get('OPENAI_API_KEY'),
    base_url="https://api.deepseek.com/v3.2_speciale_expires_on_20251215")

response = client.chat.completions.create(
    model="deepseek-reasoner",
    messages=[
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": "Hello"},
    ],
    stream=False
)

print(response.choices[0].message.content)
```
