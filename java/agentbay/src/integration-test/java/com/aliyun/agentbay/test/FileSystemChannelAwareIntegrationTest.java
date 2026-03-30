package com.aliyun.agentbay.test;

import com.aliyun.agentbay.AgentBay;
import com.aliyun.agentbay.filesystem.FileSystem;
import com.aliyun.agentbay.model.BoolResult;
import com.aliyun.agentbay.model.FileContentResult;
import com.aliyun.agentbay.session.CreateSessionParams;
import com.aliyun.agentbay.session.Session;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;

import static org.junit.Assert.*;

/**
 * Integration tests verifying that FileSystem read/write operations work correctly
 * via the HTTP (LinkUrl) channel without chunking.
 */
public class FileSystemChannelAwareIntegrationTest {

    private static final String TEST_PATH_PREFIX = "/tmp";

    private AgentBay agentBay;
    private Session session;
    private FileSystem fs;

    @Before
    public void setUp() throws Exception {
        String apiKey = System.getenv("AGENTBAY_API_KEY");
        assertNotNull("AGENTBAY_API_KEY environment variable must be set", apiKey);

        agentBay = new AgentBay(apiKey);

        CreateSessionParams params = new CreateSessionParams();
        params.setImageId("linux_latest");

        session = agentBay.create(params).getSession();
        assertNotNull("Session should be created successfully", session);

        fs = session.getFileSystem();
        assertNotNull("FileSystem should be available", fs);

        logChannelInfo();
    }

    @After
    public void tearDown() throws Exception {
        if (session != null) {
            try {
                agentBay.delete(session);
            } catch (Exception e) {
                System.err.println("Warning: Error deleting session: " + e.getMessage());
            }
        }
    }

    private void logChannelInfo() {
        String linkUrl = session.getLinkUrl();
        String token = session.getToken();
        if (linkUrl != null && !linkUrl.isEmpty() && token != null && !token.isEmpty()) {
            System.out.println("[Channel] Using HTTP (LinkUrl) channel");
        } else {
            System.out.println("[Channel] Using MQTT (API) channel");
        }
    }

    @Test
    public void testSmallFileRoundtrip() throws Exception {
        String content = "Hello, channel-aware filesystem!";
        String path = TEST_PATH_PREFIX + "/channel_test_small.txt";

        BoolResult writeResult = fs.writeFile(path, content, "overwrite", false);
        assertTrue("WriteFile should succeed", writeResult.isSuccess());

        FileContentResult readResult = fs.readFile(path);
        assertTrue("ReadFile should succeed", readResult.isSuccess());
        assertEquals("Content should match", content, readResult.getContent());

        System.out.println("[PASS] Small file roundtrip: " + content.length() + " bytes");
    }

    @Test
    public void testMediumFileRoundtrip() throws Exception {
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < 60 * 1024; i++) {
            sb.append('A');
        }
        String content = sb.toString();
        String path = TEST_PATH_PREFIX + "/channel_test_medium.txt";

        BoolResult writeResult = fs.writeFile(path, content, "overwrite", false);
        assertTrue("WriteFile should succeed", writeResult.isSuccess());

        FileContentResult readResult = fs.readFile(path);
        assertTrue("ReadFile should succeed", readResult.isSuccess());
        assertEquals("Content length should match", content.length(), readResult.getContent().length());

        System.out.println("[PASS] Medium file roundtrip: " + content.length() + " bytes");
    }

    @Test
    public void testLargeFileRoundtrip() throws Exception {
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < 200 * 1024; i++) {
            sb.append('B');
        }
        String content = sb.toString();
        String path = TEST_PATH_PREFIX + "/channel_test_large.txt";

        BoolResult writeResult = fs.writeFile(path, content, "overwrite", false);
        assertTrue("WriteFile should succeed", writeResult.isSuccess());

        FileContentResult readResult = fs.readFile(path);
        assertTrue("ReadFile should succeed", readResult.isSuccess());
        assertEquals("Content length should match", content.length(), readResult.getContent().length());

        System.out.println("[PASS] Large file roundtrip: " + content.length() + " bytes");
    }

    @Test
    public void testAppendMode() throws Exception {
        String path = TEST_PATH_PREFIX + "/channel_test_append.txt";

        BoolResult writeResult = fs.writeFile(path, "first part", "overwrite", false);
        assertTrue("Initial WriteFile should succeed", writeResult.isSuccess());

        BoolResult appendResult = fs.writeFile(path, " second part", "append", false);
        assertTrue("Append WriteFile should succeed", appendResult.isSuccess());

        FileContentResult readResult = fs.readFile(path);
        assertTrue("ReadFile should succeed", readResult.isSuccess());
        assertEquals("Appended content should match", "first part second part", readResult.getContent());

        System.out.println("[PASS] Append mode works correctly");
    }

    @Test
    public void testUnicodeContent() throws Exception {
        String content = "\u4f60\u597d\u4e16\u754c \uD83C\uDF0D \u3053\u3093\u306b\u3061\u306f \uc548\ub155\ud558\uc138\uc694 \u0645\u0631\u062d\u0628\u0627";
        String path = TEST_PATH_PREFIX + "/channel_test_unicode.txt";

        BoolResult writeResult = fs.writeFile(path, content, "overwrite", false);
        assertTrue("WriteFile should succeed", writeResult.isSuccess());

        FileContentResult readResult = fs.readFile(path);
        assertTrue("ReadFile should succeed", readResult.isSuccess());
        assertEquals("Unicode content should match", content, readResult.getContent());

        System.out.println("[PASS] Unicode content roundtrip");
    }
}
