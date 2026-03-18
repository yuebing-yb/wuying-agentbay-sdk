package com.aliyun.agentbay.skills;

import com.aliyun.agentbay.AgentBay;
import org.junit.Test;

import java.util.Arrays;
import java.util.List;

import static org.junit.Assert.*;

/**
 * Integration tests for BetaSkills.getMetadata() via GetSkillMetaData POP action.
 *
 * This test uses real backend resources (no mocks). Do not run concurrently.
 */
public class BetaSkillsGetMetadataIntegrationTest {

    @Test
    public void testGetMetadataReturnsSkillsRootPath() throws Exception {
        String apiKey = System.getenv("AGENTBAY_API_KEY");
        if (apiKey == null || apiKey.isEmpty()) {
            return;
        }

        AgentBay agentBay = new AgentBay(apiKey);
        SkillsMetadataResult result = agentBay.getBetaSkills().getMetadata();

        assertNotNull(result);
        assertNotNull(result.getSkillsRootPath());
        assertTrue(result.getSkillsRootPath().length() > 0);
        assertNotNull(result.getSkills());
    }

    @Test
    public void testGetMetadataWithGroupIdsFilter() throws Exception {
        String apiKey = System.getenv("AGENTBAY_API_KEY");
        if (apiKey == null || apiKey.isEmpty()) {
            return;
        }

        AgentBay agentBay = new AgentBay(apiKey);
        List<String> groupIds = Arrays.asList("5kvAvffm");
        SkillsMetadataResult result = agentBay.getBetaSkills().getMetadata(null, groupIds);

        assertNotNull(result);
        assertNotNull(result.getSkills());
        assertNotNull(result.getSkillsRootPath());
    }

    @Test
    public void testGetMetadataWithImageId() throws Exception {
        String apiKey = System.getenv("AGENTBAY_API_KEY");
        if (apiKey == null || apiKey.isEmpty()) {
            return;
        }

        AgentBay agentBay = new AgentBay(apiKey);
        SkillsMetadataResult result = agentBay.getBetaSkills().getMetadata("linux_latest", null);

        assertNotNull(result);
        assertNotNull(result.getSkillsRootPath());
        assertTrue(result.getSkillsRootPath().length() > 0);
    }
}
