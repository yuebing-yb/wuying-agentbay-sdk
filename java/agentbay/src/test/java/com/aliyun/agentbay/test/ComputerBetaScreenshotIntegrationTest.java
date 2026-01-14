package com.aliyun.agentbay.test;

import com.aliyun.agentbay.AgentBay;
import com.aliyun.agentbay.model.ScreenshotBytesResult;
import com.aliyun.agentbay.session.CreateSessionParams;
import com.aliyun.agentbay.model.SessionResult;
import com.aliyun.agentbay.session.Session;
import org.junit.Test;

import static org.junit.Assert.*;

/**
 * Integration test for Computer.betaTakeScreenshot().
 *
 * This test uses real backend resources (no mocks). Do not run concurrently.
 */
public class ComputerBetaScreenshotIntegrationTest {

    @Test
    public void testComputerBetaScreenshotJpeg() throws Exception {
        String apiKey = System.getenv("AGENTBAY_API_KEY");
        if (apiKey == null || apiKey.isEmpty()) {
            return;
        }

        AgentBay agentBay = new AgentBay(apiKey);
        CreateSessionParams params = new CreateSessionParams();
        params.setImageId("linux_latest");
        SessionResult create = agentBay.create(params);
        assertTrue(create.isSuccess());
        Session session = create.getSession();
        assertNotNull(session);

        try {
            Thread.sleep(10000);
            ScreenshotBytesResult s = session.getComputer().betaTakeScreenshot("jpg");
            assertTrue(s.isSuccess());
            assertEquals("jpeg", s.getFormat());
            assertNotNull(s.getData());
            assertTrue(s.getData().length > 3);
            assertEquals((byte) 0xff, s.getData()[0]);
            assertEquals((byte) 0xd8, s.getData()[1]);
            assertEquals((byte) 0xff, s.getData()[2]);
        } finally {
            agentBay.delete(session, false);
        }
    }
}

