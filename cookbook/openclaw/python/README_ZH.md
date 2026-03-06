# OpenClaw 会话管理示例

本示例展示如何在 AgentBay 上创建 OpenClaw 会话，并通过 AgentBay Context 实现配置持久化。

## 前置条件

运行脚本**仅需**通过 `export` 设置环境变量：

- `AGENTBAY_API_KEY`（必需）

```bash
# 设置 API Key
export AGENTBAY_API_KEY=your_api_key_here

# 安装依赖
pip install wuying-agentbay-sdk
```

---

## 一、基础使用（Basic Use）

直接启动脚本，不带额外参数：

```bash
python main.py
```

脚本会创建 OpenClaw 会话并启动 dashboard。启动完成后，可通过 **resource_url（沙箱流化界面）** 访问 OpenClaw WebUI：

- 控制台会输出 `Desktop URL`（即 resource_url）
- 在浏览器中打开该 URL，进入 AgentBay 云桌面
- 在云桌面内，OpenClaw dashboard 已在后台运行，可通过本地地址（如 `http://127.0.0.1:端口`）访问 OpenClaw WebUI

按 `Ctrl+C` 退出并释放会话。

![基础使用 - 沙箱流化界面访问 OpenClaw WebUI](images/image_04.png)

---

## 二、高级使用（Advanced Use）

执行脚本时附带 `--expose-web` 参数，可将 OpenClaw WebUI 转发到沙箱外部，在本地浏览器直接访问：

```bash
python main.py --expose-web
```

### 前置要求

- **AgentBay 版本**：需开通 AgentBay 的 **Pro** 或 **Ultra** 版本，才支持 `get_link` 外部链接能力
- **端口限制**：出于安全管控考虑，AgentBay `get_link` 仅支持端口范围 **30100–30199**
- **Gateway 端口**：脚本会自动将 OpenClaw gateway 默认端口修改为 30100，并配置 `bind: lan`、`controlUi.allowedOrigins` 等，以支持非 loopback 访问

### 输出说明

启动成功后，控制台会输出 `External Dashboard URL`，即可在本地浏览器直接访问的 HTTPS 地址，格式示例：

```
https://gateway.xxx.com/request_ai/xxx/#token=xxx
```

![External Dashboard URL 示例](images/image.png)

---

## 三、通过 WebUI 配置频道与模型

启动 OpenClaw WebUI 后，可在控制台中配置**频道**和**模型**，无需预先设置相关环境变量。目前支持的频道包括：

- **飞书（Feishu）**：需配置 App ID、App Secret 等
- **钉钉（DingTalk）**：需配置 Client ID、Client Secret 等

模型配置（如通义千问等）同样可在 WebUI 的「代理」-「模型」中完成，无需 `DASHSCOPE_API_KEY` 等环境变量。

**代理与模型配置界面：**

![OpenClaw 代理与模型配置](images/image_02.png)

**频道配置界面（飞书 / 钉钉）：**

![OpenClaw 频道配置](images/image_01.png)

---

## 四、AgentBay Context 与 OpenClaw 镜像的配合使用

脚本默认启用 **AgentBay Context** 实现数据持久化，与 OpenClaw 镜像配合使用，可在多次会话之间保留配置与数据。

### 同步路径

- **Context 路径**：`/home/wuying/.openclaw`
- **默认 Context 名称**：`openclaw-files`

### 持久化内容

- OpenClaw 配置文件（`openclaw.json`）
- Skills、插件等扩展
- 工作区与会话相关数据

### 工作流程

1. 首次创建会话时，若 Context 不存在则自动创建
2. 会话启动时，将 Context 中的 `/home/wuying/.openclaw` 同步到镜像内
3. 会话运行期间，对 OpenClaw 配置的修改会回写至 Context
4. 会话销毁后，Context 中的数据保留，下次创建会话时可继续使用

---

## 输出示例

```
Initializing AgentBay client...
Getting/creating context: openclaw-files
Context ID: SdkCtx-xxx
Creating session with context sync (path: /home/wuying/.openclaw)...
Session created successfully, Session ID: s-xxx

============================================================
Session Information:
============================================================
  Session ID:    s-xxx
  Context Name:  openclaw-files
  Context ID:    SdkCtx-xxx
  External Dashboard URL: https://gateway.xxx.com/request_ai/xxx/#token=xxx  # 仅 --expose-web 时
  Desktop URL:   https://wy.aliyuncs.com/app/xxx
============================================================

Press Ctrl+C to exit and release the session.
```
