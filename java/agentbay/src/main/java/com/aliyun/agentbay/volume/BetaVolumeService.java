package com.aliyun.agentbay.volume;

import com.aliyun.agentbay.AgentBay;
import com.aliyun.agentbay.exception.AgentBayException;
import com.aliyun.agentbay.model.OperationResult;
import com.aliyun.agentbay.util.ResponseUtil;
import com.aliyun.wuyingai20250506.models.DeleteVolumeRequest;
import com.aliyun.wuyingai20250506.models.DeleteVolumeResponse;
import com.aliyun.wuyingai20250506.models.GetVolumeRequest;
import com.aliyun.wuyingai20250506.models.GetVolumeResponse;
import com.aliyun.wuyingai20250506.models.ListVolumesRequest;
import com.aliyun.wuyingai20250506.models.ListVolumesResponse;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

/**
 * Beta volume service (trial feature).
 */
public class BetaVolumeService {
    private final AgentBay agentBay;

    public BetaVolumeService(AgentBay agentBay) {
        this.agentBay = agentBay;
    }

    public VolumeResult betaGetByName(String name, String imageId, boolean create) throws AgentBayException {
        if (name == null || name.trim().isEmpty()) {
            throw new IllegalArgumentException("name is required");
        }
        if (imageId == null || imageId.trim().isEmpty()) {
            throw new IllegalArgumentException("imageId is required");
        }

        try {
            GetVolumeRequest req = new GetVolumeRequest();
            req.setAuthorization("Bearer " + agentBay.getApiKey());
            req.setAllowCreate(create);
            req.setImageId(imageId);
            req.setVolumeName(name);

            GetVolumeResponse resp = agentBay.client.getVolume(req);
            String requestId = ResponseUtil.extractRequestId(resp);

            VolumeResult result = new VolumeResult();
            result.setRequestId(requestId);

            if (resp == null || resp.getBody() == null) {
                result.setSuccess(false);
                result.setErrorMessage("Empty response body");
                return result;
            }

            if (Boolean.FALSE.equals(resp.getBody().getSuccess()) && resp.getBody().getCode() != null) {
                result.setSuccess(false);
                String code = resp.getBody().getCode();
                String message = resp.getBody().getMessage() != null ? resp.getBody().getMessage() : "Unknown error";
                result.setErrorMessage("[" + code + "] " + message);
                return result;
            }

            if (resp.getBody().getData() == null || resp.getBody().getData().getVolumeId() == null) {
                result.setSuccess(false);
                result.setErrorMessage("VolumeId not found in response");
                return result;
            }

            Volume v = new Volume();
            v.setId(resp.getBody().getData().getVolumeId());
            v.setName(resp.getBody().getData().getVolumeName());
            v.setBelongingImageId(resp.getBody().getData().getBelongingImageId());
            v.setStatus(resp.getBody().getData().getStatus());
            v.setCreatedAt(resp.getBody().getData().getCreateTime());

            result.setSuccess(true);
            result.setVolume(v);
            result.setErrorMessage("");
            return result;
        } catch (Exception e) {
            throw new AgentBayException("Failed to get volume", e);
        }
    }

    public VolumeListResult betaList(String imageId, Integer maxResults, String nextToken, List<String> volumeIds, String volumeName) throws AgentBayException {
        if (imageId == null || imageId.trim().isEmpty()) {
            throw new IllegalArgumentException("imageId is required");
        }
        int max = (maxResults != null && maxResults > 0) ? maxResults : 10;

        try {
            ListVolumesRequest req = new ListVolumesRequest();
            req.setAuthorization("Bearer " + agentBay.getApiKey());
            req.setImageId(imageId);
            req.setMaxResults(max);
            if (nextToken != null && !nextToken.isEmpty()) {
                req.setNextToken(nextToken);
            }
            if (volumeIds != null && !volumeIds.isEmpty()) {
                req.setVolumeIds(volumeIds);
            }
            if (volumeName != null && !volumeName.isEmpty()) {
                req.setVolumeName(volumeName);
            }

            ListVolumesResponse resp = agentBay.client.listVolumes(req);
            String requestId = ResponseUtil.extractRequestId(resp);

            VolumeListResult result = new VolumeListResult();
            result.setRequestId(requestId);

            if (resp == null || resp.getBody() == null) {
                result.setSuccess(false);
                result.setErrorMessage("Empty response body");
                result.setVolumes(Collections.emptyList());
                return result;
            }

            if (Boolean.FALSE.equals(resp.getBody().getSuccess()) && resp.getBody().getCode() != null) {
                result.setSuccess(false);
                String code = resp.getBody().getCode();
                String message = resp.getBody().getMessage() != null ? resp.getBody().getMessage() : "Unknown error";
                result.setErrorMessage("[" + code + "] " + message);
                result.setVolumes(Collections.emptyList());
                return result;
            }

            List<Volume> volumes = new ArrayList<>();
            if (resp.getBody().getData() != null) {
                for (com.aliyun.wuyingai20250506.models.ListVolumesResponseBody.ListVolumesResponseBodyData it : resp.getBody().getData()) {
                    if (it == null || it.getVolumeId() == null) {
                        continue;
                    }
                    Volume v = new Volume();
                    v.setId(it.getVolumeId());
                    v.setName(it.getVolumeName());
                    v.setBelongingImageId(it.getBelongingImageId());
                    v.setStatus(it.getStatus());
                    v.setCreatedAt(it.getCreateTime());
                    volumes.add(v);
                }
            }

            result.setSuccess(true);
            result.setVolumes(volumes);
            result.setNextToken(resp.getBody().getNextToken());
            result.setMaxResults(resp.getBody().getMaxResults());
            result.setTotalCount(volumes.size());
            result.setErrorMessage("");
            return result;
        } catch (Exception e) {
            throw new AgentBayException("Failed to list volumes", e);
        }
    }

    public OperationResult betaDelete(String volumeId) throws AgentBayException {
        if (volumeId == null || volumeId.trim().isEmpty()) {
            throw new IllegalArgumentException("volumeId is required");
        }
        try {
            DeleteVolumeRequest req = new DeleteVolumeRequest();
            req.setAuthorization("Bearer " + agentBay.getApiKey());
            req.setVolumeId(volumeId);
            DeleteVolumeResponse resp = agentBay.client.deleteVolume(req);
            String requestId = ResponseUtil.extractRequestId(resp);

            OperationResult result = new OperationResult();
            result.setRequestId(requestId);

            if (resp == null || resp.getBody() == null) {
                result.setSuccess(false);
                result.setErrorMessage("Empty response body");
                return result;
            }

            if (Boolean.FALSE.equals(resp.getBody().getSuccess()) && resp.getBody().getCode() != null) {
                String code = resp.getBody().getCode();
                String message = resp.getBody().getMessage() != null ? resp.getBody().getMessage() : "Unknown error";
                result.setSuccess(false);
                result.setErrorMessage("[" + code + "] " + message);
                return result;
            }

            result.setSuccess(true);
            result.setErrorMessage("");
            return result;
        } catch (Exception e) {
            throw new AgentBayException("Failed to delete volume", e);
        }
    }
}


