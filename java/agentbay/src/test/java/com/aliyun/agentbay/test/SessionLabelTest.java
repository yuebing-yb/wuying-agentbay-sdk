package com.aliyun.agentbay.test;

import com.aliyun.agentbay.AgentBay;
import com.aliyun.agentbay.exception.AgentBayException;
import com.aliyun.agentbay.model.OperationResult;
import com.aliyun.agentbay.model.SessionResult;
import com.aliyun.agentbay.session.CreateSessionParams;
import com.aliyun.agentbay.session.Session;
import org.junit.jupiter.api.*;

import java.util.HashMap;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.*;

/**
 * Test cases for Session label management (setLabels and getLabels methods)
 */
@TestMethodOrder(MethodOrderer.OrderAnnotation.class)
public class SessionLabelTest {

    private static AgentBay agentBay;
    private static Session session;

    @BeforeAll
    public static void setup() throws Exception {
        String apiKey = System.getenv("AGENTBAY_API_KEY");
        assertNotNull(apiKey, "AGENTBAY_API_KEY environment variable must be set");

        agentBay = new AgentBay();

        // Create a test session
        CreateSessionParams params = new CreateSessionParams();
        params.setImageId("linux_latest");
        SessionResult result = agentBay.create(params);
        assertTrue(result.isSuccess(), "Failed to create test session");
        session = result.getSession();
        assertNotNull(session, "Session should not be null");
    }

    @AfterAll
    public static void tearDown() {
        if (session != null) {
            session.delete();
        }
    }

    @Test
    @Order(1)
    @DisplayName("Test setLabels - Basic functionality")
    public void testSetLabelsBasic() throws AgentBayException {
        Map<String, String> labels = new HashMap<>();
        labels.put("environment", "test");
        labels.put("team", "qa");
        labels.put("project", "agentbay-sdk");

        OperationResult result = session.setLabels(labels);

        assertTrue(result.isSuccess(), "setLabels should succeed");
        assertNotNull(result.getRequestId(), "Request ID should not be null");
        assertNotNull(result.getData(), "Data should not be null");

        @SuppressWarnings("unchecked")
        Map<String, String> returnedLabels = (Map<String, String>) result.getData();
        assertEquals(3, returnedLabels.size(), "Should return 3 labels");
        assertEquals("test", returnedLabels.get("environment"));
        assertEquals("qa", returnedLabels.get("team"));
        assertEquals("agentbay-sdk", returnedLabels.get("project"));
    }

    @Test
    @Order(2)
    @DisplayName("Test getLabels - Retrieve previously set labels")
    public void testGetLabels() throws AgentBayException {
        OperationResult result = session.getLabels();

        assertTrue(result.isSuccess(), "getLabels should succeed");
        assertNotNull(result.getRequestId(), "Request ID should not be null");
        assertNotNull(result.getData(), "Data should not be null");

        @SuppressWarnings("unchecked")
        Map<String, String> labels = (Map<String, String>) result.getData();

        // Should have at least the labels we set in test 1
        assertTrue(labels.size() >= 3, "Should have at least 3 labels");
        assertEquals("test", labels.get("environment"));
        assertEquals("qa", labels.get("team"));
        assertEquals("agentbay-sdk", labels.get("project"));
    }

    @Test
    @Order(3)
    @DisplayName("Test setLabels - Update existing labels")
    public void testUpdateLabels() throws AgentBayException {
        // Update environment label and add new label
        Map<String, String> labels = new HashMap<>();
        labels.put("environment", "production");  // Update existing
        labels.put("version", "v1.0.0");          // Add new

        OperationResult setResult = session.setLabels(labels);
        assertTrue(setResult.isSuccess(), "setLabels should succeed");

        // Verify changes
        OperationResult getResult = session.getLabels();
        assertTrue(getResult.isSuccess(), "getLabels should succeed");

        @SuppressWarnings("unchecked")
        Map<String, String> retrievedLabels = (Map<String, String>) getResult.getData();

        assertEquals("production", retrievedLabels.get("environment"), "Environment should be updated");
        assertEquals("v1.0.0", retrievedLabels.get("version"), "Version should be added");
        assertEquals("qa", retrievedLabels.get("team"), "Team should still exist");
        assertEquals("agentbay-sdk", retrievedLabels.get("project"), "Project should still exist");
    }

    @Test
    @Order(4)
    @DisplayName("Test setLabels - Empty labels map")
    public void testSetEmptyLabels() throws AgentBayException {
        Map<String, String> emptyLabels = new HashMap<>();

        OperationResult result = session.setLabels(emptyLabels);

        assertTrue(result.isSuccess(), "Setting empty labels should succeed");
    }

    @Test
    @Order(5)
    @DisplayName("Test setLabels - Null labels throws exception")
    public void testSetNullLabels() {
        AgentBayException exception = assertThrows(AgentBayException.class, () -> {
            session.setLabels(null);
        });

        assertTrue(exception.getMessage().contains("Labels cannot be null"),
                "Exception message should mention null labels");
    }

    @Test
    @Order(6)
    @DisplayName("Test setLabels - Too many labels (>20)")
    public void testTooManyLabels() {
        Map<String, String> manyLabels = new HashMap<>();
        for (int i = 0; i < 21; i++) {
            manyLabels.put("key" + i, "value" + i);
        }

        AgentBayException exception = assertThrows(AgentBayException.class, () -> {
            session.setLabels(manyLabels);
        });

        assertTrue(exception.getMessage().contains("Maximum 20 labels"),
                "Exception message should mention maximum labels limit");
    }

    @Test
    @Order(7)
    @DisplayName("Test setLabels - Label key too long (>128 chars)")
    public void testLabelKeyTooLong() {
        String longKey = "k".repeat(129);
        Map<String, String> labels = new HashMap<>();
        labels.put(longKey, "value");

        AgentBayException exception = assertThrows(AgentBayException.class, () -> {
            session.setLabels(labels);
        });

        assertTrue(exception.getMessage().contains("cannot exceed 128 characters"),
                "Exception message should mention key length limit");
    }

    @Test
    @Order(8)
    @DisplayName("Test setLabels - Label value too long (>256 chars)")
    public void testLabelValueTooLong() {
        String longValue = "v".repeat(257);
        Map<String, String> labels = new HashMap<>();
        labels.put("key", longValue);

        AgentBayException exception = assertThrows(AgentBayException.class, () -> {
            session.setLabels(labels);
        });

        assertTrue(exception.getMessage().contains("cannot exceed 256 characters"),
                "Exception message should mention value length limit");
    }

    @Test
    @Order(9)
    @DisplayName("Test setLabels - Empty label key throws exception")
    public void testEmptyLabelKey() {
        Map<String, String> labels = new HashMap<>();
        labels.put("", "value");

        AgentBayException exception = assertThrows(AgentBayException.class, () -> {
            session.setLabels(labels);
        });

        assertTrue(exception.getMessage().contains("cannot be null or empty"),
                "Exception message should mention empty key");
    }

    @Test
    @Order(10)
    @DisplayName("Test setLabels - Null label value is allowed")
    public void testNullLabelValue() throws AgentBayException {
        Map<String, String> labels = new HashMap<>();
        labels.put("nullable-key", null);

        OperationResult result = session.setLabels(labels);

        assertTrue(result.isSuccess(), "Setting null value should succeed");
    }

    @Test
    @Order(11)
    @DisplayName("Test setLabels - Special characters in labels")
    public void testSpecialCharactersInLabels() throws AgentBayException {
        Map<String, String> labels = new HashMap<>();
        labels.put("env-name", "test-env");
        labels.put("team.name", "backend.team");
        labels.put("project_name", "agentbay_sdk");
        labels.put("version:tag", "v1.0.0:latest");

        OperationResult result = session.setLabels(labels);

        assertTrue(result.isSuccess(), "Setting labels with special characters should succeed");

        // Verify retrieval
        OperationResult getResult = session.getLabels();
        @SuppressWarnings("unchecked")
        Map<String, String> retrievedLabels = (Map<String, String>) getResult.getData();

        assertEquals("test-env", retrievedLabels.get("env-name"));
        assertEquals("backend.team", retrievedLabels.get("team.name"));
        assertEquals("agentbay_sdk", retrievedLabels.get("project_name"));
        assertEquals("v1.0.0:latest", retrievedLabels.get("version:tag"));
    }

    @Test
    @Order(12)
    @DisplayName("Test setLabels - Maximum valid label key length (128 chars)")
    public void testMaxValidKeyLength() throws AgentBayException {
        String maxKey = "k".repeat(128);
        Map<String, String> labels = new HashMap<>();
        labels.put(maxKey, "value");

        OperationResult result = session.setLabels(labels);

        assertTrue(result.isSuccess(), "Setting 128-char key should succeed");
    }

    @Test
    @Order(13)
    @DisplayName("Test setLabels - Maximum valid label value length (256 chars)")
    public void testMaxValidValueLength() throws AgentBayException {
        String maxValue = "v".repeat(256);
        Map<String, String> labels = new HashMap<>();
        labels.put("key", maxValue);

        OperationResult result = session.setLabels(labels);

        assertTrue(result.isSuccess(), "Setting 256-char value should succeed");
    }

    @Test
    @Order(14)
    @DisplayName("Test label lifecycle - Set, get, update, get")
    public void testLabelLifecycle() throws AgentBayException {
        // Step 1: Set initial labels
        Map<String, String> initialLabels = new HashMap<>();
        initialLabels.put("stage", "initial");
        initialLabels.put("count", "1");

        session.setLabels(initialLabels);

        // Step 2: Verify initial labels
        OperationResult getResult1 = session.getLabels();
        @SuppressWarnings("unchecked")
        Map<String, String> labels1 = (Map<String, String>) getResult1.getData();
        assertEquals("initial", labels1.get("stage"));
        assertEquals("1", labels1.get("count"));

        // Step 3: Update labels
        Map<String, String> updateLabels = new HashMap<>();
        updateLabels.put("stage", "updated");
        updateLabels.put("count", "2");
        updateLabels.put("new-label", "added");

        session.setLabels(updateLabels);

        // Step 4: Verify updated labels
        OperationResult getResult2 = session.getLabels();
        @SuppressWarnings("unchecked")
        Map<String, String> labels2 = (Map<String, String>) getResult2.getData();
        assertEquals("updated", labels2.get("stage"), "Stage should be updated");
        assertEquals("2", labels2.get("count"), "Count should be updated");
        assertEquals("added", labels2.get("new-label"), "New label should be added");
    }
}
