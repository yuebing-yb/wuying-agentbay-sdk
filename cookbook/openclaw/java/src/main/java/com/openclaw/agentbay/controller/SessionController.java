package com.openclaw.agentbay.controller;

import com.openclaw.agentbay.model.CreateSessionRequest;
import com.openclaw.agentbay.model.SessionResponse;
import com.openclaw.agentbay.service.SessionManager;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

/**
 * 会话管理 REST API
 */
@RestController
@RequestMapping("/api/sessions")
public class SessionController {

    private final SessionManager sessionManager;

    public SessionController(SessionManager sessionManager) {
        this.sessionManager = sessionManager;
    }

    /**
     * 创建一个新的 OpenClaw 沙箱会话
     *
     * 流程: 创建沙箱 -> 写入配置 -> 启动 Gateway -> 打开 Dashboard -> 返回 resource_url
     */
    @PostMapping
    public ResponseEntity<?> createSession(@RequestBody CreateSessionRequest request) {
        // 参数校验
        if (isBlank(request.getAgentbayApiKey())) {
            return badRequest("agentbayApiKey 不能为空");
        }
        if (isBlank(request.getBailianApiKey())) {
            return badRequest("bailianApiKey 不能为空");
        }
        if (isBlank(request.getUsername())) {
            return badRequest("username 不能为空");
        }

        try {
            SessionResponse response = sessionManager.createSession(request);
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(Map.of("detail", e.getMessage()));
        }
    }

    /**
     * 查询指定会话状态
     */
    @GetMapping("/{sessionId}")
    public ResponseEntity<?> getSession(@PathVariable String sessionId) {
        SessionResponse response = sessionManager.getSession(sessionId);
        if (response == null) {
            return ResponseEntity.status(HttpStatus.NOT_FOUND)
                    .body(Map.of("detail", "会话不存在"));
        }
        return ResponseEntity.ok(response);
    }

    /**
     * 销毁指定会话
     */
    @DeleteMapping("/{sessionId}")
    public ResponseEntity<?> deleteSession(@PathVariable String sessionId) {
        boolean success = sessionManager.deleteSession(sessionId);
        if (!success) {
            return ResponseEntity.status(HttpStatus.NOT_FOUND)
                    .body(Map.of("detail", "会话不存在"));
        }
        return ResponseEntity.ok(Map.of(
                "message", "会话已销毁",
                "sessionId", sessionId
        ));
    }

    /**
     * 列出所有活跃会话
     */
    @GetMapping
    public ResponseEntity<List<SessionResponse>> listSessions() {
        return ResponseEntity.ok(sessionManager.listSessions());
    }

    private boolean isBlank(String s) {
        return s == null || s.trim().isEmpty();
    }

    private ResponseEntity<Map<String, String>> badRequest(String message) {
        return ResponseEntity.badRequest().body(Map.of("detail", message));
    }
}
