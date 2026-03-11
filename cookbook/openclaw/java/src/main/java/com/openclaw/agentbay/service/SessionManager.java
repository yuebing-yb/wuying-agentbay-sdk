package com.openclaw.agentbay.service;

import com.aliyun.agentbay.AgentBay;
import com.aliyun.agentbay.context.*;
import com.aliyun.agentbay.model.CommandResult;
import com.aliyun.agentbay.model.OperationResult;
import com.aliyun.agentbay.model.SessionInfoResult;
import com.aliyun.agentbay.model.SessionStatusResult;
import com.aliyun.agentbay.model.SessionResult;
import com.aliyun.agentbay.session.CreateSessionParams;
import com.aliyun.agentbay.session.Session;
import com.openclaw.agentbay.model.CreateSessionRequest;
import com.openclaw.agentbay.model.SessionInfo;
import com.openclaw.agentbay.model.SessionResponse;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

/**
 * 会话管理器
 *
 * 负责创建、查询、销毁 OpenClaw 沙箱会话。
 * 所有会话数据保存在内存中 (ConcurrentHashMap)，不使用数据库。
 */
@Service
public class SessionManager {

    private static final Logger log = LoggerFactory.getLogger(SessionManager.class);

    /** 预装 OpenClaw 的 AgentBay 镜像 ID */
    private static final String OPENCLAW_IMAGE_ID = "openclaw-linux-ubuntu-2204";

    /** 沙箱中 OpenClaw 配置文件路径 */
    private static final String CONFIG_PATH = "/home/wuying/.openclaw/openclaw.json";

    /** Gateway 端口 (开放策略，与 openclaw.json 中一致) */
    private static final int GATEWAY_PORT = 30100;

    /** Gateway 认证 Token */
    private static final String GATEWAY_TOKEN = "4decb1b9ff4997825eb91e37bf28798e0af1f7f00c6b4b1c";

    /** 持久化 Context 挂载路径 */
    private static final String CONTEXT_SYNC_PATH = "/home/wuying/.openclaw/";

    private final ConfigBuilder configBuilder;

    /** 内存中的活跃会话存储 */
    private final Map<String, SessionInfo> activeSessions = new ConcurrentHashMap<>();

    public SessionManager(ConfigBuilder configBuilder) {
        this.configBuilder = configBuilder;
    }

    /**
     * 创建一个新的 OpenClaw 沙箱会话
     *
     * 流程:
     * 1. 创建 AgentBay Session (使用前端传入的 API Key)
     * 2. 检测沙箱中可用的 bot 命令
     * 3. 生成并写入 openclaw.json 配置
     * 4. 停止旧 gateway -> 后台启动新 gateway
     * 5. 等待 gateway 就绪
     * 6. 通过 getLink 获取 OpenClaw UI 外部链接
     * 7. 返回 resource_url + openclawUrl
     */
    public SessionResponse createSession(CreateSessionRequest request) {
        log.info("正在为用户 {} 创建 AgentBay 会话...", request.getUsername());

        // 1. 使用前端传入的 API Key 创建客户端，并配置 Context 持久化
        AgentBay agentBay;
        Session session;
        try {
            agentBay = new AgentBay(request.getAgentbayApiKey());

            // 根据用户名获取或创建持久化 Context
            String contextName = "openclaw-" + request.getUsername();
            log.info("正在获取/创建持久化 Context: {}", contextName);
            ContextResult contextResult = agentBay.getContext().get(contextName, true);
            if (!contextResult.isSuccess()) {
                throw new RuntimeException("获取 Context 失败: " + contextResult.getErrorMessage());
            }
            String contextId = contextResult.getContext().getId();
            log.info("Context 就绪: id={}", contextId);

            // 配置压缩模式的同步策略
            SyncPolicy syncPolicy = SyncPolicy.defaultPolicy();
            syncPolicy.getUploadPolicy().setUploadMode(UploadMode.ARCHIVE);
            syncPolicy.getExtractPolicy().setDeleteSrcFile(true);
            syncPolicy.getExtractPolicy().setExtractCurrentFolder(true);
            syncPolicy.getExtractPolicy().setExtract(true);

            ContextSync contextSync = ContextSync.create(contextId, CONTEXT_SYNC_PATH, syncPolicy)
                    .withBetaWaitForCompletion(true);

            CreateSessionParams params = new CreateSessionParams();
            params.setImageId(OPENCLAW_IMAGE_ID);
            params.setContextSyncs(Arrays.asList(contextSync));

            SessionResult result = agentBay.create(params);
            if (!result.isSuccess()) {
                throw new RuntimeException("创建会话失败: " + result.getErrorMessage());
            }
            session = result.getSession();
        } catch (RuntimeException e) {
            throw e;
        } catch (Exception e) {
            throw new RuntimeException("创建会话失败: " + e.getMessage(), e);
        }
        log.info("会话创建成功: {}", session.getSessionId());

        try {
            // 2. bot 命令固定为 openclaw
            String botCmd = "openclaw";

            // 3. 生成配置并写入沙箱
            log.info("正在写入 OpenClaw 配置文件...");
            String configJson = configBuilder.build(
                    request.getBailianApiKey(),
                    request.getDingtalkClientId(),
                    request.getDingtalkClientSecret(),
                    request.getFeishuAppId(),
                    request.getFeishuAppSecret(),
                    request.getModelBaseUrl(),
                    request.getModelId()
            );
            // FileSystem.write() 返回 String，失败时抛出 AgentBayException
            session.getFileSystem().write(CONFIG_PATH, configJson);
            log.info("配置文件写入成功");

            // 4. 停止旧 gateway
            log.info("正在停止旧 gateway 进程...");
            executeCmd(session, "openclaw gateway stop; pkill -f 'openclaw gateway' || true", 10000);

            // 5. 后台启动新 gateway
            log.info("正在后台启动 gateway...");
            executeCmd(session,
                    "bash -lc 'nohup " + botCmd + " gateway > /tmp/gateway.log 2>&1 &'",
                    15000);

            // 6. 等待 gateway 就绪并在沙箱内打开 dashboard
            String dashboardUrl = "http://127.0.0.1:" + GATEWAY_PORT + "/#token=" + GATEWAY_TOKEN;
            log.info("正在等待 gateway 就绪...");
            executeCmd(session,
                    "bash -lc '"
                            + "for i in $(seq 1 15); do "
                            + "curl -fsS http://127.0.0.1:" + GATEWAY_PORT + " >/dev/null 2>&1 && break; "
                            + "sleep 2; "
                            + "done; "
                            + "nohup firefox \"" + dashboardUrl + "\" >/dev/null 2>&1 &"
                            + "'",
                    60000);

            // 7. 通过 getLink 获取 OpenClaw UI 外部访问链接
            String openclawUrl = "";
            try {
                OperationResult linkResult = session.getLink("https", GATEWAY_PORT);
                if (linkResult.isSuccess()) {
                    openclawUrl = linkResult.getData() + "/#token=" + GATEWAY_TOKEN;
                    log.info("OpenClaw UI 链接: {}", openclawUrl);
                } else {
                    log.warn("获取 OpenClaw UI 链接失败: {}", linkResult.getErrorMessage());
                }
            } catch (Exception e) {
                log.warn("获取 OpenClaw UI 链接异常: {}", e.getMessage());
            }

            // 8. 保存到内存并返回
            String now = LocalDateTime.now().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME);
            SessionInfo info = new SessionInfo(
                    session.getSessionId(),
                    session.getResourceUrl() != null ? session.getResourceUrl() : "",
                    openclawUrl,
                    request.getUsername(),
                    now,
                    "running",
                    agentBay,
                    session
            );

            activeSessions.put(session.getSessionId(), info);

            log.info("会话启动完成! sessionId={}, resourceUrl={}",
                    session.getSessionId(), session.getResourceUrl());

            return toResponse(info);

        } catch (Exception e) {
            log.error("会话创建过程中出错，正在清理...", e);
            try {
                session.delete();
            } catch (Exception ignored) {
            }
            throw new RuntimeException("创建会话失败: " + e.getMessage(), e);
        }
    }

    /**
     * 查询会话状态
     */
    public SessionResponse getSession(String sessionId) {
        SessionInfo info = activeSessions.get(sessionId);
        return info != null ? toResponse(info) : null;
    }

    /**
     * 销毁会话
     */
    public boolean deleteSession(String sessionId) {
        SessionInfo info = activeSessions.remove(sessionId);
        if (info == null) {
            return false;
        }
        try {
            if (info.getSession() != null) {
                // delete(true) 会自动同步 Context 数据后再销毁
                info.getSession().delete(true);
                log.info("会话 {} 已销毁（Context 已同步）", sessionId);
            }
        } catch (Exception e) {
            log.error("销毁会话 {} 时出错: {}", sessionId, e.getMessage());
        }
        return true;
    }

    /**
     * 列出所有活跃会话
     */
    public List<SessionResponse> listSessions() {
        List<SessionResponse> list = new ArrayList<>();
        for (SessionInfo info : activeSessions.values()) {
            list.add(toResponse(info));
        }
        return list;
    }

    // ── 内部方法 ──────────────────────────────────────────

    private void executeCmd(Session session, String cmd, int timeoutMs) {
        log.debug("执行命令: {}", cmd);
        CommandResult result = session.getCommand().executeCommand(cmd, timeoutMs);
        if (!result.isSuccess()) {
            log.error("命令执行失败: " + result.getErrorMessage());
        }
        if (result.getOutput() != null && !result.getOutput().isEmpty()) {
            log.debug("命令输出: {}", result.getOutput().substring(0, Math.min(200, result.getOutput().length())));
        }
    }

    private SessionResponse toResponse(SessionInfo info) {
        return new SessionResponse(
                info.getSessionId(),
                info.getResourceUrl(),
                info.getOpenclawUrl(),
                info.getUsername(),
                info.getCreatedAt(),
                info.getStatus()
        );
    }
}
