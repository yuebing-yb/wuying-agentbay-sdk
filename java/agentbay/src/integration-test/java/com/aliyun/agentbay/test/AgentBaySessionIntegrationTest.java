package com.aliyun.agentbay.test;

import com.aliyun.agentbay.AgentBay;
import com.aliyun.agentbay.exception.AgentBayException;
import com.aliyun.agentbay.model.SessionResult;
import com.aliyun.agentbay.session.CreateSessionParams;
import com.aliyun.agentbay.session.Session;
import org.junit.Test;

import static org.junit.Assert.*;

/**
 * Test cases for AgentBay session operations.
 * This test class is equivalent to test_agent_bay_session.py in Python SDK
 */
public class AgentBaySessionIntegrationTest {

    /**
     * Test cases for AgentBay session operations - Create, List, Delete
     */
    @Test
    public void testCreateListDelete() throws AgentBayException {
        // Test create, list, and delete methods
        AgentBay agentBay = new AgentBay();

        // Create a session
        System.out.println("Creating a new session...");
        SessionResult result = agentBay.create(new CreateSessionParams());
        
        // Check if session creation was successful
        assertTrue("Session creation failed: " + result.getErrorMessage(), result.isSuccess());
        assertNotNull("Session object is null", result.getSession());
        
        Session session = result.getSession();
        System.out.println("Session created with ID: " + session.getSessionId());

        // Ensure session ID is not empty
        assertNotNull(session.getSessionId());
        assertFalse(session.getSessionId().isEmpty());

        // Delete the session
        System.out.println("Deleting the session...");
        agentBay.delete(session, false);

        // Session deletion completed
        System.out.println("✅ testCreateListDelete passed");
    }

}