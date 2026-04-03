// ci-stable
package com.aliyun.agentbay.test;

import com.aliyun.agentbay.AgentBay;
import com.aliyun.agentbay.skills.SkillMetadata;
import org.junit.Test;

import java.util.List;

import static org.junit.Assert.*;

/**
 * Integration test for BetaSkills.listMetadata().
 *
 * This test uses real backend resources (no mocks). Do not run concurrently.
 */
public class BetaSkillsMetadataIntegrationTest {

    @Test
    public void testBetaSkillsListMetadata() throws Exception {
        String apiKey = System.getenv("AGENTBAY_API_KEY");
        if (apiKey == null || apiKey.isEmpty()) {
            return;
        }

        AgentBay agentBay = new AgentBay(apiKey);
        List<SkillMetadata> items = agentBay.getBetaSkills().listMetadata();
        assertNotNull(items);
        assertTrue(items.size() > 0);
        SkillMetadata first = items.get(0);
        assertNotNull(first.getName());
        assertTrue(first.getName().trim().length() > 0);
        assertNotNull(first.getDescription());
        assertNull(first.getDir());
    }
}

