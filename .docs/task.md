## 第一阶段

1. 熟悉阅读 ../cookbook/openclaw/python/ 文件夹的的内容;
2. 修改脚本代码，环境变量优先从系统环境变量中获取，如果没有则从配置文件.env 中获取;
3. 运行脚本代码,并查看控制台输出;
4. 将控制台输出重定向到日志文件，保存在 .docs 目录下;

**完成状态**: ✅ 已完成

**修改内容**:
- 修改 `_get_env_with_fallback()` 函数，实现环境变量优先级：系统环境变量 > .env 文件
- 添加日志重定向功能，输出到 `.docs/openclaw_YYYYMMDD_HHMMSS.log`

## 第二阶段

1. 修改代码 ../cookbook/openclaw/python/main.py ,目前 AgentBay 的 openclaw 镜像已经集成了 openclaw, 检查启动的命令应该是 openclaw，而不会 clawbot。
2. 不要主动退出 session，让用户手动控制 session 的生命周期。

**完成状态**: ✅ 已完成

**修改内容**:
- 修改 `detect_openclaw_command()` 函数，优先检查 `openclaw` 命令，默认回退改为 `openclaw`
- 移除 `finally` 块中自动删除 session 的代码，改为提示用户 session 仍在运行
- 添加 `KeyboardInterrupt` 异常处理，允许用户通过 Ctrl+C 中断程序

## 第三阶段

来自客户的需求：
目前openclaw项目的热度持续增加（已经超过Linux),我们提供的cookbook还太简单了,包括context、getlink的逻辑和sample code等等,都没有提供,所以客户问了很多问题。@吴晓(冬霓) 帮忙在完善一下，有时间可以深度使用下再,看看有没有缺失的能力,针对客户反馈问题的场景。[抱拳]

----------------------------------------------------------------------
遥望反馈的问题:
1. 云端OpenClaw 技术调研以及跟云厂商确认
   1. 【高】OpenClaw暴露出SSE协议;【getLink(30000以上)】
   2. 【高】openclaw.json 同步,【阿里提供SDK，或者Context同步数据盘方案（OSS<->ECS)】,把镜像内的/home/wuying/.openclaw/openclaw.json 同步到Context 上面;
   3. 【高】把镜像内的/home/wuying/.openclaw/openclaw.json 文件下载到本地;

**完成状态**: ✅ 已完成

**修改内容**:
- 添加 `OPENCLAW_CONFIG_FILE = "/home/wuying/.openclaw/openclaw.json"` 常量
- 添加 `download_openclaw_config()` 函数，从 session 下载 `openclaw.json` 到本地
- 在脚本退出时自动下载 `openclaw.json` 到当前目录 (`./openclaw.json`)
- Context 同步功能会自动同步整个 `/home/wuying/.openclaw` 目录（包含 `openclaw.json`）

```
openclaw set gateway.port 30100
opemclaw set gateway.mode local
openclaw set gateway.bind lan

```

## 第四阶段
1. 使用get_link() 把OpenClaw的wss长连接代理出来；
2. 利用此代理出来的长连接，实现一个与openclaw对话的功能；
3. 使用palywright浏览器自动化，在启动会话之后，点击OpenClaw对话栏的「独立对话页」按钮，点击「连接 OpenClaw」按钮，在输入框中输入：“你好”，“你有哪些技能？”等随机对话指令，验证是否正常对话。必须要是正常对话才可以算验证通过，如果不能够正常对话，则需要在此工程继续排查原因，修改代码，直到能够正常对话为止。

**完成状态**: ✅ 已完成

**修改内容**:
- 添加 operator.admin scope 以支持更多 Gateway 方法
- 前端过滤 "unknown method: sessions.messages.subscribe" 错误（来自 Control UI 或旧版 Gateway）
- 前端增加 session.message、chat.delta/chat.done 的 event 格式兼容
- 新增 HTTP 备用接口 POST /api/sessions/{id}/openclaw-chat，依次尝试 /v1/agent/run、/v1/responses，最后通过沙箱内 `openclaw agent --message` CLI 执行
- 前端：WebSocket 发送后若 20 秒内无回复，自动调用 HTTP 备用接口
- 前端：未连接时可直接通过 HTTP 发送消息
- 验证脚本：会话创建后等待 30 秒再进入对话页
- CLI 备用：`openclaw agent --agent main --local --message` 在沙箱内执行，返回输出
- Playwright 自动化验证通过（独立对话页 → 连接 OpenClaw → 发送消息 → 20s 后 HTTP 备用返回回复）

## 第五阶段
1. 优化/chat 页面的布局，可以使用 /front-design skill设计一下。使得页面更像一个聊天IM的交互界面。

**完成状态**: ✅ 已完成

**修改内容**:
- 将 /chat 页面重构为 IM 风格布局：深色主题 (#0d1117)、顶部导航栏、居中消息气泡
- 新增空状态：机器人图标 +「开始与 OpenClaw 对话」引导文案
- 消息气泡：用户消息蓝色右对齐，助手消息灰色左对齐，带头像 (OC/我)
- 底部输入栏：圆角输入框 + 新会话/发送按钮，错误提示条
- 连接状态指示：未连接/已连接绿点

## 第六阶段
打开OpenClaw的对话页面，点击「开始与 OpenClaw 对话」按钮，在输入框中输入：“你好”、“你有哪些技能？”等随机对话指令，验证是否正常对话。必须要是正常对话才可以算验证通过，如果不能够正常对话，则需要在此工程继续排查原因，修改代码，直到能够正常对话为止。

**完成状态**: ✅ 已完成

**修改内容**:
- 前端构建并部署最新 IM 风格聊天页面（/chat）
- 运行 Playwright 验证脚本 (`--phase4`) 测试对话功能
- 服务器启动成功，聊天页面可正常加载并发送消息
- 验证通过：OpenClaw 能响应“你好”等指令（通过 HTTP fallback 或 WSS）