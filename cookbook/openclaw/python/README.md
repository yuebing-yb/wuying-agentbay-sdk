# OpenClaw in AgentBay (Python)

一键创建 OpenClaw 沙箱环境的示例工程，基于 Python FastAPI 后端 + React 前端。

## 功能

- 通过 AgentBay SDK 创建沙箱会话，自动部署 OpenClaw
- 支持 Context 持久化（基于用户名，ARCHIVE 压缩模式）
- 通过 `getLink` 获取 OpenClaw UI 外部访问链接
- 支持自定义模型 Base URL 和模型 ID
- **钉钉 / 飞书机器人一键配置**：会话创建成功后，可自动完成扫码登录、创建应用、提取凭证并回填到 OpenClaw 配置
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
│   ├── session_manager.py # 会话管理核心
│   ├── dingtalk_setup.py # 钉钉一键配置入口（三种后端统一调度）
│   ├── dingtalk_setup_common.py # 钉钉共享类型和工具函数
│   ├── dingtalk_setup_playwright.py # 钉钉 Playwright 实现（默认）
│   ├── dingtalk_setup_browser_operator.py # 钉钉 Browser Operator 实现
│   ├── dingtalk_setup_browser_agent.py # 钉钉 BrowserUseAgent 实现
│   ├── feishu_setup.py # 飞书一键配置入口
│   ├── feishu_setup_common.py # 飞书共享类型和工具函数
│   └── feishu_setup_playwright.py # 飞书 Playwright 实现
├── frontend/            # React 前端源码
│   ├── src/
│   │   ├── App.tsx      # 主应用组件
│   │   └── components/
│   │       ├── SessionForm.tsx      # 创建会话表单
│   │       ├── DingtalkSetupPanel.tsx # 钉钉一键配置面板
│   │       └── FeishuSetupPanel.tsx # 飞书一键配置面板
│   ├── package.json
│   └── vite.config.ts
├── static/              # 前端构建产物
├── images/              # 文档图片
├── requirements.txt
└── README.md
```

### 一键配置钉钉 / 飞书机器人

会话创建成功后，可点击「一键配置钉钉机器人」或「一键配置飞书机器人」，系统将在沙箱内自动打开浏览器，引导完成扫码登录、创建应用、提取凭证并回填到 OpenClaw 配置。

**钉钉配置流程：**

1. **开始配置**：打开钉钉开放平台并展示二维码
2. **扫码登录**：使用钉钉 APP 扫描右侧云机中的二维码
3. **我已登录**：登录成功后点击，系统自动创建应用并提取 Client ID、Client Secret
4. **提交并更新配置**：将凭证写入 OpenClaw 配置并重启 Gateway

**飞书配置流程：**

1. **开始配置**：打开飞书开放平台并展示二维码
2. **扫码登录**：使用飞书 APP 扫描右侧云机中的二维码
3. **我已登录**：登录成功后点击，系统自动创建企业自建应用、添加机器人能力、开通权限、配置事件订阅（长连接）、版本发布并提取 App ID、App Secret
4. **提交并更新配置**：将凭证写入 OpenClaw 配置并重启 Gateway

### 前端开发

前端源码位于 `frontend/` 目录，使用 React + Vite + TypeScript。

```bash
# 安装依赖
cd frontend
npm install

# 开发模式（热重载，API 代理到 localhost:8080）
npm run dev

# 构建生产版本
npm run build
```

构建后需将 `frontend/dist/` 目录内容复制到 `static/`：

```bash
cp -r frontend/dist/* static/
```

## API

### 会话管理

| 方法   | 路径                    | 说明       |
|--------|------------------------|-----------|
| POST   | `/api/sessions`        | 创建会话   |
| GET    | `/api/sessions/{id}`   | 查询会话   |
| DELETE | `/api/sessions/{id}`   | 销毁会话   |
| GET    | `/api/sessions`        | 列出所有会话 |

### 钉钉一键配置

| 方法   | 路径                                         | 说明                     |
|--------|---------------------------------------------|-------------------------|
| POST   | `/api/sessions/{id}/dingtalk-setup/start`   | 启动配置（打开登录页）     |
| POST   | `/api/sessions/{id}/dingtalk-setup/continue`| 继续配置（登录后创建应用） |
| GET    | `/api/sessions/{id}/dingtalk-setup/status`  | 获取配置状态             |
| POST   | `/api/sessions/{id}/dingtalk-setup/apply`   | 应用凭证到 OpenClaw 配置  |

### 飞书一键配置

| 方法   | 路径                                         | 说明                     |
|--------|---------------------------------------------|-------------------------|
| POST   | `/api/sessions/{id}/feishu-setup/start`     | 启动配置（打开登录页）     |
| POST   | `/api/sessions/{id}/feishu-setup/continue`  | 继续配置（登录后创建应用） |
| GET    | `/api/sessions/{id}/feishu-setup/status`    | 获取配置状态             |
| POST   | `/api/sessions/{id}/feishu-setup/apply`   | 应用凭证到 OpenClaw 配置  |

API 文档：`http://localhost:8080/docs`

---

## 会话功能说明

### Context 持久化

创建会话时填写**用户名称**，系统会为该用户启用 AgentBay Context 持久化，使 OpenClaw 的配置、Skills、插件和工作区数据在会话销毁后仍可保留，下次创建会话时自动恢复。

#### 什么是 Context？

Context 是 AgentBay 提供的**持久化存储容器**，与临时会话不同：

| 特性 | 会话 (Session) | Context |
|------|----------------|---------|
| 生命周期 | 临时，销毁即消失 | 持久，需手动删除才清除 |
| 数据存储 | 不保存 | 持久保存 |
| 共享 | 独立 | 可被多个会话挂载使用 |

#### 本项目的 Context 配置

- **Context 名称**：`openclaw-{用户名}`（按用户名隔离，同一用户多次创建会话共享同一 Context）
- **挂载路径**：`/home/wuying/.openclaw`（沙箱内 OpenClaw 数据目录）
- **同步策略**：ARCHIVE 压缩模式（上传前压缩，适合配置、Skills、插件等文本类文件）
- **持久化内容**：OpenClaw 配置、Skills、插件、工作区数据

#### 同步流程

1. **会话创建时**：从 Context 下载数据到挂载路径，OpenClaw 可直接使用已有配置
2. **会话运行中**：对 `/home/wuying/.openclaw` 的读写与普通文件操作一致
3. **会话销毁时**：将挂载路径下的变更上传回 Context，供下次会话使用

#### 使用建议

- **销毁会话时确保同步完成**：调用 `agent_bay.delete(session, sync_context=True)`，等待上传完成后再返回，避免新会话拿不到最新数据
- **大量文件写入后**：可显式调用 `session.context.sync()` 触发上传，再销毁会话
- **多会话连续创建**：若需立即用新会话访问刚写入的数据，务必使用 `sync_context=True` 或先 `sync()` 再 `delete`

### 外部访问链接

会话创建成功后，返回的 `openclawUrl` 为 OpenClaw UI 的外部 HTTPS 链接，可直接在本地浏览器访问。

**前置要求**：AgentBay Pro 或 Ultra 版本，`getLink` 默认支持端口 30100–30199。如需开放其他端口，可发邮件至 agentbay_dev@alibabacloud.com 申请加白名单。

---

## 对接 AgentBay OpenClaw 沙箱的常见问题与解决方案

### 1. 沙箱保活问题

**问题描述**：用户使用 OpenClaw「养龙虾」，体现一个「养」字——龙虾需要根据用户的记忆和习惯逐渐自进化出具有个性化的特性，因此保存龙虾的运行环境和用户数据至关重要。沙箱长时间无操作可能被回收，导致会话中断、环境丢失。

**解决方案**：

- **控制台配置**：AgentBay 支持在阿里云控制台的「策略配置 → 生命周期管理」中设置**桌面单次运行最长时间**（最长 1000 分钟）和**休眠超期时长**（最长 72 小时）。启用「释放不活跃桌面」后，MCP 和用户交互均满足终止时间后，系统将自动释放不活跃桌面。
- **长期保活**：有强烈需求长期保活的用户，可在阿里云控制台提交工单，申请加入白名单，开通长期保活能力。

![策略配置 - 生命周期管理](images/image_01.png)

### 2. 用户数据同步问题

**问题描述**：会话销毁后，新会话中用户数据未正确恢复或出现数据不一致。

**解决方案**：使用 AgentBay 的 Context 数据持久化能力，在创建会话时挂载 Context，将 OpenClaw 数据目录（`/home/wuying/.openclaw`）与 Context 绑定，实现跨会话数据自动同步。核心实现如下：

```python
from agentbay import AgentBay, ContextSync, CreateSessionParams, SyncPolicy, UploadMode

# 按用户名获取或创建持久化 Context（同一用户多次创建会话共享同一 Context）
context_name = f"openclaw-{request.username}"
context_result = agent_bay.context.get(context_name, create=True)
if not context_result.success:
    raise RuntimeError(f"Failed to get Context: {context_result.error_message}")
context_id = context_result.context.id

# 配置同步策略：ARCHIVE 压缩模式，适合配置、Skills、插件等文本类文件
sync_policy = SyncPolicy.default()
sync_policy.upload_policy.upload_mode = UploadMode.ARCHIVE
sync_policy.extract_policy.delete_src_file = True
sync_policy.extract_policy.extract_current_folder = True
sync_policy.extract_policy.extract = True

# 创建 Context 同步配置：将 Context 挂载到 OpenClaw 数据目录
context_sync = ContextSync.new(
    context_id=context_id,
    path="/home/wuying/.openclaw",  # 沙箱内 OpenClaw 数据目录
    policy=sync_policy,
    beta_wait_for_completion=True,  # 等待 Context 下载完成后再返回会话
)

# 创建会话时绑定 Context
params = CreateSessionParams(image_id=OPENCLAW_IMAGE_ID)
params.context_syncs = [context_sync]
session_result = agent_bay.create(params)
```

销毁会话时建议使用 `agent_bay.delete(session, sync_context=True)`，确保数据上传完成后再返回。

**场景选择建议**：

| 场景 | 同步策略 | 上传模式 |
|------|----------|----------|
| OpenClaw 配置、插件等文本数据（本项目默认） | 默认（自动上传/下载） | ARCHIVE（压缩，节省带宽与存储） |
| 小量配置文件 | 默认 | FILE（原样上传） |
| 只读数据集（如预置模型） | 仅下载 | 按需选择 |
| 需精确控制同步时机 | 手动同步 + 显式调用 `session.context.sync()` | 按需选择 |

### 3. 定制自定义镜像

**问题描述**：若需在 OpenClaw 镜像中预装各类依赖（如部分 Skills 依赖的 npm 包、Python 的 pip 包等），并希望这些安装包在会话间持久存在，Context 仅适用于文件级数据同步，不适用于系统级安装包持久化，此时可通过**定制自定义镜像**解决。

**解决方案**：参见阿里云文档 [创建并管理自定义镜像的完整生命周期](https://help.aliyun.com/zh/agentbay/manage-images/)。
