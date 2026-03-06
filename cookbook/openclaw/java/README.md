# OpenClaw in AgentBay (Java)

一键创建 OpenClaw 沙箱环境的示例工程，基于 Java Spring Boot 后端 + React 前端。

## 功能

- 通过 AgentBay SDK 创建沙箱会话，自动部署 OpenClaw
- 支持 Context 持久化（基于用户名，ARCHIVE 压缩模式）
- 通过 `getLink` 获取 OpenClaw UI 外部访问链接
- 支持自定义模型 Base URL 和模型 ID
- 前端静态文件内嵌 Spring Boot，单进程运行

## 快速开始

### 环境要求

- Java 17+
- Maven 3.8+

### 运行

```bash
# 编译并启动
mvn clean compile
mvn spring-boot:run
```

访问 `http://localhost:8080` 打开管理页面。

### 修改前端（可选）

如需修改前端页面：

```bash
cd frontend
npm install
npm run build
cp -r dist/* ../src/main/resources/static/
```

然后重新编译运行后端即可。

## 项目结构

```
java/
├── pom.xml                          # Maven 配置
├── src/main/
│   ├── java/com/openclaw/agentbay/
│   │   ├── Application.java         # Spring Boot 入口
│   │   ├── WebConfig.java           # CORS 配置
│   │   ├── controller/
│   │   │   └── SessionController.java  # REST API
│   │   ├── model/
│   │   │   ├── CreateSessionRequest.java
│   │   │   ├── SessionInfo.java
│   │   │   └── SessionResponse.java
│   │   └── service/
│   │       ├── ConfigBuilder.java    # OpenClaw 配置生成
│   │       └── SessionManager.java   # 会话管理核心
│   └── resources/
│       ├── application.properties
│       └── static/                   # 前端构建产物
├── frontend/                         # 前端源码 (React + Vite)
│   ├── src/
│   │   ├── App.tsx
│   │   ├── App.css
│   │   └── components/
│   │       └── SessionForm.tsx
│   └── package.json
└── README.md
```

## API

| 方法   | 路径                    | 说明       |
|--------|------------------------|-----------|
| POST   | `/api/sessions`        | 创建会话   |
| GET    | `/api/sessions/{id}`   | 查询会话   |
| DELETE | `/api/sessions/{id}`   | 销毁会话   |
| GET    | `/api/sessions`        | 列出所有会话 |
