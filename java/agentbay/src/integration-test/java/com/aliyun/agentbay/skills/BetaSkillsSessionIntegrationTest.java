package com.aliyun.agentbay.skills;

import com.aliyun.agentbay.AgentBay;
import com.aliyun.agentbay.exception.AgentBayException;
import com.aliyun.agentbay.model.DeleteResult;
import com.aliyun.agentbay.session.CreateSessionParams;
import com.aliyun.agentbay.session.Session;
import org.junit.Test;

import static org.junit.Assert.*;

/**
 * Integration tests for session creation with skills loading.
 *
 * This test uses real backend resources (no mocks). Do not run concurrently.
 */
public class BetaSkillsSessionIntegrationTest {

    @Test
    public void testCreateSessionWithLoadSkills() throws Exception {
        String apiKey = System.getenv("AGENTBAY_API_KEY");
        if (apiKey == null || apiKey.isEmpty()) {
            return;
        }

        AgentBay agentBay = new AgentBay(apiKey);
        CreateSessionParams params = new CreateSessionParams();
        params.setLoadSkills(true);

        com.aliyun.agentbay.model.SessionResult result = agentBay.create(params);
        assertTrue(result.isSuccess());
        assertNotNull(result.getSession());

        Session session = result.getSession();
        try {
            assertNotNull(session.getSessionId());
        } finally {
            DeleteResult deleteResult = agentBay.delete(session, false);
            assertTrue(deleteResult.isSuccess());
        }
    }

    @Test
    public void testCreateSessionWithoutSkills() throws AgentBayException {
        String apiKey = System.getenv("AGENTBAY_API_KEY");
        if (apiKey == null || apiKey.isEmpty()) {
            return;
        }

        AgentBay agentBay = new AgentBay(apiKey);
        CreateSessionParams params = new CreateSessionParams();

        com.aliyun.agentbay.model.SessionResult result = agentBay.create(params);
        assertTrue(result.isSuccess());
        assertNotNull(result.getSession());

        Session session = result.getSession();
        try {
            // Only verify session creation without loadSkills succeeds
        } finally {
            DeleteResult deleteResult = agentBay.delete(session, false);
            assertTrue(deleteResult.isSuccess());
        }
    }
}
