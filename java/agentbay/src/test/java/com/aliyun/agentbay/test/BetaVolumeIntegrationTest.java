package com.aliyun.agentbay.test;

import com.aliyun.agentbay.AgentBay;
import com.aliyun.agentbay.exception.AgentBayException;
import com.aliyun.agentbay.model.OperationResult;
import com.aliyun.agentbay.model.SessionResult;
import com.aliyun.agentbay.session.CreateSessionParams;
import com.aliyun.agentbay.session.Session;
import com.aliyun.agentbay.volume.VolumeListResult;
import com.aliyun.agentbay.volume.VolumeResult;
import org.junit.Test;

import static org.junit.Assert.*;

public class BetaVolumeIntegrationTest {

    @Test
    public void testBetaVolumeCreateListMountAndDelete() throws Exception {
        AgentBay agentBay = new AgentBay();

        String imageId = "imgc-0ab5ta4mgqs15qxjf";
        String volumeName = "beta-volume-it-" + System.currentTimeMillis();

        VolumeResult createResult = agentBay.getBetaVolume().betaGetByName(volumeName, imageId, true);
        assertTrue("expected volume create/get success", createResult.isSuccess());
        assertNotNull("expected volume not null", createResult.getVolume());
        assertNotNull("expected volume id", createResult.getVolume().getId());
        String volumeId = createResult.getVolume().getId();

        try {
            VolumeListResult listResult = agentBay.getBetaVolume().betaList(imageId, 10, null, null, volumeName);
            assertTrue("expected list success", listResult.isSuccess());
            assertTrue(
                "expected created volume to be listed",
                listResult.getVolumes().stream().anyMatch(v -> volumeId.equals(v.getId()))
            );

            CreateSessionParams params = new CreateSessionParams();
            params.setImageId(imageId);
            params.setVolumeId(volumeId);

            SessionResult sessionResult = agentBay.create(params);
            assertTrue("expected session create success", sessionResult.isSuccess());
            assertNotNull("expected session not null", sessionResult.getSession());
            Session session = sessionResult.getSession();
            assertNotNull("expected token not null", session.getToken());

            agentBay.delete(session, false);
        } finally {
            OperationResult delResult = agentBay.getBetaVolume().betaDelete(volumeId);
            assertTrue("expected delete volume success", delResult.isSuccess());
        }
    }
}


