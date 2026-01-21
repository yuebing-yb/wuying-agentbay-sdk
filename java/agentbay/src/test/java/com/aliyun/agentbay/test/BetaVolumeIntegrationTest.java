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
        assertNotNull("expected volume status not null", createResult.getVolume().getStatus());
        assertFalse("expected volume status not empty", createResult.getVolume().getStatus().isEmpty());
        String volumeId = createResult.getVolume().getId();

        try {
            VolumeListResult listResult = agentBay.getBetaVolume().betaList(imageId, 10, null, null, volumeName);
            assertTrue("expected list success", listResult.isSuccess());
            assertTrue(
                "expected listed volume to have non-empty status",
                listResult.getVolumes().stream()
                    .filter(v -> volumeId.equals(v.getId()))
                    .allMatch(v -> v.getStatus() != null && !v.getStatus().isEmpty())
            );
            assertTrue(
                "expected created volume to be listed",
                listResult.getVolumes().stream().anyMatch(v -> volumeId.equals(v.getId()))
            );

            VolumeResult getById = agentBay.getBetaVolume().betaGetById(volumeId, imageId);
            assertTrue("expected get by id success", getById.isSuccess());
            assertNotNull("expected get by id volume not null", getById.getVolume());
            assertNotNull("expected get by id volume status not null", getById.getVolume().getStatus());
            assertFalse("expected get by id volume status not empty", getById.getVolume().getStatus().isEmpty());

            CreateSessionParams params = new CreateSessionParams();
            params.setImageId(imageId);
            params.setBetaVolumeId(volumeId);

            SessionResult sessionResult = agentBay.create(params);
            assertTrue("expected session create success", sessionResult.isSuccess());
            assertNotNull("expected session not null", sessionResult.getSession());
            Session session = sessionResult.getSession();
            assertNotNull("expected session id not null", session.getSessionId());

            agentBay.delete(session, false);
        } finally {
            OperationResult delResult = agentBay.getBetaVolume().betaDelete(volumeId);
            assertTrue("expected delete volume success", delResult.isSuccess());
        }
    }
}


