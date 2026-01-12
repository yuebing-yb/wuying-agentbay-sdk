package com.aliyun.agentbay.examples;

import com.aliyun.agentbay.AgentBay;
import com.aliyun.agentbay.model.DeleteResult;
import com.aliyun.agentbay.model.SessionResult;
import com.aliyun.agentbay.model.UIElementListResult;
import com.aliyun.agentbay.session.CreateSessionParams;
import com.aliyun.agentbay.session.Session;

/**
 * Mobile GetAllUiElements (XML) Example
 *
 * This example demonstrates how to retrieve raw XML UI hierarchy via
 * Mobile.getAllUiElements(timeoutMs, "xml").
 */
public class MobileGetAllUiElementsXmlExample {

    public static void main(String[] args) throws Exception {
        String apiKey = System.getenv("AGENTBAY_API_KEY");
        if (apiKey == null || apiKey.isEmpty()) {
            System.err.println("AGENTBAY_API_KEY environment variable is not set");
            System.exit(1);
        }

        AgentBay agentBay = new AgentBay();
        CreateSessionParams params = new CreateSessionParams();
        params.setImageId("imgc-0ab5takhnlaixj11v");

        SessionResult sessionResult = agentBay.create(params);
        if (!sessionResult.isSuccess() || sessionResult.getSession() == null) {
            throw new RuntimeException("Failed to create session: " + sessionResult.getErrorMessage());
        }

        Session session = sessionResult.getSession();
        try {
            Thread.sleep(15000);
            UIElementListResult ui = session.mobile.getAllUiElements(10000, "xml");
            if (!ui.isSuccess()) {
                throw new RuntimeException("getAllUiElements(xml) failed: " + ui.getErrorMessage());
            }

            System.out.println("RequestID: " + ui.getRequestId());
            System.out.println("Format: " + ui.getFormat());
            System.out.println("Raw length: " + ui.getRaw().length());
            System.out.println("Elements: " + ui.getElements().size());
        } finally {
            DeleteResult deleteResult = agentBay.delete(session, false);
            System.out.println("Session deleted. Success: " + deleteResult.isSuccess());
        }
    }
}

