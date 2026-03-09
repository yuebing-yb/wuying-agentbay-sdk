# OpenClaw in AgentBay (Python)

一键创建 OpenClaw 沙箱环境的示例工程，基于 Python FastAPI 后端 + React 前端。

## 功能

- 通过 AgentBay SDK 创建沙箱会话，自动部署 OpenClaw
- 支持 Context 持久化（基于用户名，ARCHIVE 压缩模式）
- 通过 `getLink` 获取 OpenClaw UI 外部访问链接
- 支持自定义模型 Base URL 和模型 ID
- 前端静态文件与 FastAPI 同目录，单进程运行

## 快速开始

### 环境要求

- Python 3.10+
- pip

### 运行

```bash
cd cookbook/openclaw/python

# 安装依赖
pip install -r requirements.txt

# 启动 Web 服务
python main.py
```

访问 `http://localhost:8080` 打开管理页面。

![OpenClaw in AgentBay - 一键创建沙箱环境](images/image_05.png)

### 启动参数（可选）

```bash
# 指定地址和端口
python main.py --host 0.0.0.0 --port 8080

# 开发模式（代码更改自动重载）
python main.py --reload
```

| 参数 | 说明 |
|------|------|
| `--host` | 绑定地址，默认 0.0.0.0 |
| `--port` | 端口，默认 8080 |
| `--reload` | 开发模式，代码更改自动重载 |

## 项目结构

```
cookbook/openclaw/python/
├── main.py              # Web 服务入口
├── src/
│   ├── __init__.py
│   ├── app.py           # FastAPI 应用
│   ├── config_builder.py # OpenClaw 配置生成
│   ├── models.py        # Pydantic 数据模型
│   └── session_manager.py # 会话管理核心
├── static/              # 前端构建产物
├── images/              # 文档图片
├── requirements.txt
├── README.md
└── README_ZH.md
```

## API

| 方法   | 路径                    | 说明       |
|--------|------------------------|-----------|
| POST   | `/api/sessions`        | 创建会话   |
| GET    | `/api/sessions/{id}`   | 查询会话   |
| DELETE | `/api/sessions/{id}`   | 销毁会话   |
| GET    | `/api/sessions`        | 列出所有会话 |

API 文档：`http://localhost:8080/docs`

---

## 会话功能说明

### Context 持久化

创建会话时填写**用户名称**，系统会为该用户启用 AgentBay Context 持久化：

- **Context 路径**：`/home/wuying/.openclaw`
- **Context 名称**：`openclaw-{用户名}`
- **持久化内容**：OpenClaw 配置、Skills、插件、工作区数据

### 外部访问链接

会话创建成功后，返回的 `openclawUrl` 为 OpenClaw UI 的外部 HTTPS 链接，可直接在本地浏览器访问。

**前置要求**：AgentBay Pro 或 Ultra 版本，`getLink` 支持端口 30100–30199。

### 频道与模型配置

启动 OpenClaw WebUI 后，可在控制台中配置**飞书**、**钉钉**等频道，以及**通义千问**等模型，无需预先设置环境变量。

![OpenClaw 代理与模型配置](images/image_02.png)

![OpenClaw 频道配置](images/image_01.png)
