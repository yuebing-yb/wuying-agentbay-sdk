package com.aliyun.agentbay.test;

import com.aliyun.agentbay.AgentBay;
import com.aliyun.agentbay.model.CommandResult;
import com.aliyun.agentbay.model.ProcessListResult;
import com.aliyun.agentbay.model.ScreenshotBytesResult;
import com.aliyun.agentbay.model.SessionResult;
import com.aliyun.agentbay.session.CreateSessionParams;
import com.aliyun.agentbay.session.Session;
import org.junit.Test;

import static org.junit.Assert.*;

/**
 * Integration test for Mobile.betaTakeScreenshot(format).
 *
 * This test uses real backend resources (no mocks). Do not run concurrently.
 */
public class MobileBetaScreenshotIntegrationTest {

    @Test
    public void testMobileBetaScreenshotJpeg() throws Exception {
        String apiKey = System.getenv("AGENTBAY_API_KEY");
        if (apiKey == null || apiKey.isEmpty()) {
            return;
        }

        AgentBay agentBay = new AgentBay(apiKey);
        CreateSessionParams params = new CreateSessionParams();
        params.setImageId("mobile-use-android-12-gw");
        SessionResult create = agentBay.create(params);
        assertTrue(create.getErrorMessage(), create.isSuccess());
        Session session = create.getSession();
        assertNotNull(session);

        try {
            Thread.sleep(15000);
            session.listMcpTools();

            CommandResult r1 = session.getCommand().executeCommand("wm size 720x1280", 10000);
            assertTrue("Command failed: " + r1.getErrorMessage(), r1.isSuccess());
            CommandResult r2 = session.getCommand().executeCommand("wm density 160", 10000);
            assertTrue("Command failed: " + r2.getErrorMessage(), r2.isSuccess());

            ProcessListResult start = session.getMobile().startApp("monkey -p com.android.settings 1");
            assertTrue("Failed to start Settings: " + start.getErrorMessage(), start.isSuccess());
            Thread.sleep(2000);

            ScreenshotBytesResult s = session.getMobile().betaTakeScreenshot("jpeg");
            assertTrue("Beta screenshot failed: " + s.getErrorMessage(), s.isSuccess());
            assertEquals("image", s.getType());
            assertEquals("image/jpeg", s.getMimeType());
            assertNotNull("Image bytes should not be null", s.getData());
            assertTrue("Image bytes should not be empty", s.getData().length > 3);
            assertNotNull("Width should not be null", s.getWidth());
            assertNotNull("Height should not be null", s.getHeight());
            assertTrue("Width should be > 0", s.getWidth() > 0);
            assertTrue("Height should be > 0", s.getHeight() > 0);
            assertEquals((byte) 0xff, s.getData()[0]);
            assertEquals((byte) 0xd8, s.getData()[1]);
            assertEquals((byte) 0xff, s.getData()[2]);
        } finally {
            agentBay.delete(session, false);
        }
    }
}

