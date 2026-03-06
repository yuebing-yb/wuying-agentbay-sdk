package com.aliyun.agentbay.agent;

import java.util.Map;

/**
 * Represents a streaming event from an Agent execution.
 *
 * <p>Event types map directly to LLM output field names:
 * <ul>
 *   <li>"reasoning": from LLM reasoning_content (model's internal reasoning/thinking)
 *   <li>"content": from LLM content (model's text output, intermediate analysis or final answer)
 *   <li>"tool_call": from LLM tool_calls (tool invocation request)
 *   <li>"tool_result": tool execution result (rich media)
 *   <li>"error": execution error
 * </ul>
 */
public class AgentEvent {
    private String type;
    private int seq;
    private int round;
    private String content;
    private String toolCallId;
    private String toolName;
    private Map<String, Object> args;
    private Map<String, Object> result;
    private Map<String, Object> error;

    public AgentEvent() {
        this.type = "";
        this.seq = 0;
        this.round = 0;
        this.content = "";
        this.toolCallId = "";
        this.toolName = "";
    }

    public AgentEvent(String type, int seq, int round) {
        this.type = type != null ? type : "";
        this.seq = seq;
        this.round = round;
        this.content = "";
        this.toolCallId = "";
        this.toolName = "";
    }

    public String getType() {
        return type;
    }

    public void setType(String type) {
        this.type = type;
    }

    public int getSeq() {
        return seq;
    }

    public void setSeq(int seq) {
        this.seq = seq;
    }

    public int getRound() {
        return round;
    }

    public void setRound(int round) {
        this.round = round;
    }

    public String getContent() {
        return content;
    }

    public void setContent(String content) {
        this.content = content;
    }

    public String getToolCallId() {
        return toolCallId;
    }

    public void setToolCallId(String toolCallId) {
        this.toolCallId = toolCallId;
    }

    public String getToolName() {
        return toolName;
    }

    public void setToolName(String toolName) {
        this.toolName = toolName;
    }

    public Map<String, Object> getArgs() {
        return args;
    }

    public void setArgs(Map<String, Object> args) {
        this.args = args;
    }

    public Map<String, Object> getResult() {
        return result;
    }

    public void setResult(Map<String, Object> result) {
        this.result = result;
    }

    public Map<String, Object> getError() {
        return error;
    }

    public void setError(Map<String, Object> error) {
        this.error = error;
    }

    @Override
    public String toString() {
        StringBuilder sb = new StringBuilder("AgentEvent{");
        sb.append("type='").append(type).append('\'');
        sb.append(", seq=").append(seq);
        sb.append(", round=").append(round);
        if (content != null && !content.isEmpty()) {
            sb.append(", content='").append(content).append('\'');
        }
        if (toolName != null && !toolName.isEmpty()) {
            sb.append(", toolName='").append(toolName).append('\'');
        }
        sb.append('}');
        return sb.toString();
    }
}
