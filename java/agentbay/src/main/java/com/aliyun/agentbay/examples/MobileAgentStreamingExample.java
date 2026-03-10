package com.aliyun.agentbay.examples;

import com.aliyun.agentbay.AgentBay;
import com.aliyun.agentbay.session.CreateSessionParams;
import com.aliyun.agentbay.session.Session;
import com.aliyun.agentbay.model.SessionResult;
import com.aliyun.agentbay.agent.StreamOptions;
import com.aliyun.agentbay.model.ExecutionResult;

import java.util.Collections;

/**
 * Mobile Agent Streaming Example
 *
 * Demonstrates:
 * 1. Mobile Agent task execution with real-time streaming output
 * 2. Using typed callbacks (onReasoning, onContent, onToolCall, onToolResult)
 */
public class MobileAgentStreamingExample {

    public static void exampleTypedCallbacks(AgentBay client) throws Exception {
        System.out.println(String.join("", Collections.nCopies(60, "=")));
        System.out.println("Example 1: Mobile Agent Streaming with Typed Callbacks");
        System.out.println(String.join("", Collections.nCopies(60, "=")));

        CreateSessionParams params = new CreateSessionParams();
        params.setImageId("imgc-0ab5takhnmlvhx9gp");
        SessionResult sessionResult = client.create(params);
        Session session = sessionResult.getSession();

        try {
            System.out.println("Session created: " + session.getSessionId());

            StreamOptions options = StreamOptions.builder()
                    .onReasoning(event ->
                            System.out.print("[Reasoning] " + event.getContent()))
                    .onContent(event ->
                            System.out.print("[Content] " + event.getContent()))
                    .onToolCall(event ->
                            System.out.println("\n[ToolCall] " + event.getToolName() + "(" + event.getArgs() + ")"))
                    .onToolResult(event ->
                            System.out.println("[ToolResult] " + event.getToolName() + " -> " + event.getResult()))
                    .build();

            ExecutionResult result = session.getAgent().getMobile()
                    .executeTaskAndWait("Open Settings app", 10, 180, options);

            System.out.println("\n\nTask completed:");
            System.out.println("  Success: " + result.isSuccess());
            System.out.println("  Status: " + result.getTaskStatus());
            if (result.getTaskResult() != null && !result.getTaskResult().isEmpty()) {
                System.out.println("  Result: " + result.getTaskResult().substring(0,
                        Math.min(200, result.getTaskResult().length())));
            }
        } finally {
            session.delete();
            System.out.println("Session cleaned up");
        }
    }

    public static void main(String[] args) throws Exception {
        System.out.println("Mobile Agent Streaming Output Examples\n");

        String apiKey = System.getenv("AGENTBAY_API_KEY");
        AgentBay client = new AgentBay(apiKey);

        exampleTypedCallbacks(client);

        System.out.println("\nAll examples completed!");
    }
}
