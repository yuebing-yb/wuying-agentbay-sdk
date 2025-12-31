package com.aliyun.agentbay.test;

import com.aliyun.agentbay.AgentBay;
import com.aliyun.agentbay.exception.AgentBayException;
import com.aliyun.agentbay.model.OperationResult;
import com.aliyun.agentbay.model.SessionResult;
import com.aliyun.agentbay.session.CreateSessionParams;
import com.aliyun.agentbay.session.Session;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.AfterClass;
import org.junit.BeforeClass;
import org.junit.FixMethodOrder;
import org.junit.Rule;
import org.junit.Test;
import org.junit.rules.ExpectedException;
import org.junit.runners.MethodSorters;

import java.util.HashMap;
import java.util.Map;

import static org.junit.Assert.*;

@FixMethodOrder(MethodSorters.NAME_ASCENDING)
public class SessionLabelTest {

    @Rule
    public ExpectedException thrown = ExpectedException.none();

    private static AgentBay agentBay;
    private static Session session;
    private static ObjectMapper objectMapper = new ObjectMapper();

    @BeforeClass
    public static void setup() throws Exception {
        String apiKey = System.getenv("AGENTBAY_API_KEY");
        assertNotNull("AGENTBAY_API_KEY environment variable must be set", apiKey);

        agentBay = new AgentBay();

        // Create a test session
        CreateSessionParams params = new CreateSessionParams();
        params.setImageId("linux_latest");
        SessionResult result = agentBay.create(params);
        assertTrue(result.isSuccess());
        session = result.getSession();
        assertNotNull(session);
    }

    @AfterClass
    public static void tearDown() {
        if (session != null) {
            session.delete();
        }
    }

    @Test
    public void test01_SetLabelsBasic() throws Exception {
        Map<String, String> labels = new HashMap<>();
        labels.put("environment", "test");
        labels.put("team", "qa");
        labels.put("project", "agentbay-sdk");

        OperationResult result = session.setLabels(labels);

        assertTrue(result.isSuccess());
        assertNotNull(result.getRequestId());
        assertNotNull(result.getData());

        Map<String, String> returnedLabels = objectMapper.readValue(
            result.getData(), new TypeReference<Map<String, String>>() {});
        assertEquals(3, returnedLabels.size());
        assertEquals("test", returnedLabels.get("environment"));
        assertEquals("qa", returnedLabels.get("team"));
        assertEquals("agentbay-sdk", returnedLabels.get("project"));
    }

    @Test
    public void test02_GetLabels() throws Exception {
        OperationResult result = session.getLabels();

        assertTrue(result.isSuccess());
        assertNotNull(result.getRequestId());
        assertNotNull(result.getData());

        Map<String, String> labels = objectMapper.readValue(
            result.getData(), new TypeReference<Map<String, String>>() {});

        assertTrue(labels.size() >= 3);
        assertEquals("test", labels.get("environment"));
        assertEquals("qa", labels.get("team"));
        assertEquals("agentbay-sdk", labels.get("project"));
    }

    @Test
    public void test03_UpdateLabels() throws Exception {
        Map<String, String> labels = new HashMap<>();
        labels.put("environment", "production");
        labels.put("version", "v1.0.0");

        OperationResult setResult = session.setLabels(labels);
        assertTrue(setResult.isSuccess());

        OperationResult getResult = session.getLabels();
        assertTrue(getResult.isSuccess());

        Map<String, String> retrievedLabels = objectMapper.readValue(
            getResult.getData(), new TypeReference<Map<String, String>>() {});

        assertEquals(2, retrievedLabels.size());
        assertEquals("production", retrievedLabels.get("environment"));
        assertEquals("v1.0.0", retrievedLabels.get("version"));
    }

    @Test
    public void test04_SetEmptyLabels() throws AgentBayException {
        Map<String, String> emptyLabels = new HashMap<>();

        OperationResult result = session.setLabels(emptyLabels);

        assertTrue(result.isSuccess());
    }

    @Test(expected = AgentBayException.class)
    public void test05_SetNullLabels() throws AgentBayException {
        session.setLabels(null);
    }

    @Test(expected = AgentBayException.class)
    public void test06_TooManyLabels() throws AgentBayException {
        Map<String, String> manyLabels = new HashMap<>();
        for (int i = 0; i < 21; i++) {
            manyLabels.put("key" + i, "value" + i);
        }
        session.setLabels(manyLabels);
    }

    @Test(expected = AgentBayException.class)
    public void test09_EmptyLabelKey() throws AgentBayException {
        Map<String, String> labels = new HashMap<>();
        labels.put("", "value");
        session.setLabels(labels);
    }

    @Test
    public void test10_NullLabelValue() throws AgentBayException {
        Map<String, String> labels = new HashMap<>();
        labels.put("nullable-key", null);

        OperationResult result = session.setLabels(labels);

        assertTrue(result.isSuccess());
    }

    @Test
    public void test11_SpecialCharactersInLabels() throws Exception {
        Map<String, String> labels = new HashMap<>();
        labels.put("env-name", "test-env");
        labels.put("team.name", "backend.team");
        labels.put("project_name", "agentbay_sdk");
        labels.put("version:tag", "v1.0.0:latest");

        OperationResult result = session.setLabels(labels);

        assertTrue(result.isSuccess());

        OperationResult getResult = session.getLabels();
        Map<String, String> retrievedLabels = objectMapper.readValue(
            getResult.getData(), new TypeReference<Map<String, String>>() {});

        assertEquals("test-env", retrievedLabels.get("env-name"));
        assertEquals("backend.team", retrievedLabels.get("team.name"));
        assertEquals("agentbay_sdk", retrievedLabels.get("project_name"));
        assertEquals("v1.0.0:latest", retrievedLabels.get("version:tag"));
    }

    @Test
    public void test14_LabelLifecycle() throws Exception {
        // Step 1: Set initial labels
        Map<String, String> initialLabels = new HashMap<>();
        initialLabels.put("stage", "initial");
        initialLabels.put("count", "1");

        session.setLabels(initialLabels);

        OperationResult getResult1 = session.getLabels();
        Map<String, String> labels1 = objectMapper.readValue(
            getResult1.getData(), new TypeReference<Map<String, String>>() {});
        assertEquals("initial", labels1.get("stage"));
        assertEquals("1", labels1.get("count"));

        // Step 3: Update labels
        Map<String, String> updateLabels = new HashMap<>();
        updateLabels.put("stage", "updated");
        updateLabels.put("count", "2");
        updateLabels.put("new-label", "added");

        session.setLabels(updateLabels);

        OperationResult getResult2 = session.getLabels();
        Map<String, String> labels2 = objectMapper.readValue(
            getResult2.getData(), new TypeReference<Map<String, String>>() {});
        assertEquals("updated", labels2.get("stage"));
        assertEquals("2", labels2.get("count"));
        assertEquals("added", labels2.get("new-label"));
    }
}
