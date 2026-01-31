package com.aliyun.agentbay.examples;

import com.aliyun.agentbay.AgentBay;
import com.aliyun.agentbay.model.OperationResult;
import com.aliyun.agentbay.model.SessionResult;
import com.aliyun.agentbay.session.CreateSessionParams;
import com.aliyun.agentbay.session.Session;

public class SessionKeepAliveExample {

    public static void main(String[] args) {
        String apiKey = System.getenv("AGENTBAY_API_KEY");
        if (apiKey == null || apiKey.trim().isEmpty()) {
            System.err.println("Please set AGENTBAY_API_KEY environment variable");
            return;
        }
        Session session = null;

        try {
            AgentBay agentBay = new AgentBay(apiKey);
            CreateSessionParams params = new CreateSessionParams();
            params.setImageId("linux_latest");
            params.setIdleReleaseTimeout(30);

            SessionResult create = agentBay.create(params);
            if (!create.isSuccess() || create.getSession() == null) {
                System.err.println("Failed to create session: " + create.getErrorMessage());
                return;
            }
            session = create.getSession();
            System.out.println("Session ID: " + session.getSessionId());

            System.out.println("Sleeping for 15 seconds...");
            Thread.sleep(15000L);

            System.out.println("Calling keepAlive() to refresh idle timer...");
            OperationResult keepAlive = session.keepAlive();
            System.out.println("keepAlive success: " + keepAlive.isSuccess());
            System.out.println("requestId: " + keepAlive.getRequestId());
            if (!keepAlive.isSuccess()) {
                System.out.println("error: " + keepAlive.getErrorMessage());
            }
        } catch (Exception e) {
            System.err.println("Error: " + e.getMessage());
            e.printStackTrace();
        } finally {
            if (session != null) {
                try {
                    session.delete(false);
                } catch (Exception ignored) {
                }
            }
        }
    }
}

