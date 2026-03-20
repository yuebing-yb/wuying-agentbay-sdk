package com.aliyun.agentbay.skills;

import com.aliyun.agentbay.AgentBay;
import com.aliyun.agentbay.exception.AgentBayException;
import com.aliyun.wuyingai20250506.models.GetSkillMetaDataRequest;
import com.aliyun.wuyingai20250506.models.GetSkillMetaDataResponse;
import com.aliyun.wuyingai20250506.models.GetSkillMetaDataResponseBody;
import com.aliyun.wuyingai20250506.models.ListSkillMetaDataRequest;
import com.aliyun.wuyingai20250506.models.ListSkillMetaDataResponse;
import com.aliyun.wuyingai20250506.models.ListSkillMetaDataResponseBody;

import java.util.ArrayList;
import java.util.List;

/**
 * Beta skills service (trial feature).
 */
public class BetaSkillsService {
    private final AgentBay agentBay;

    public BetaSkillsService(AgentBay agentBay) {
        this.agentBay = agentBay;
    }

    /**
     * Get skills metadata without starting a sandbox.
     *
     * @return SkillsMetadataResult with skills list and skillsRootPath
     * @throws AgentBayException if the API call fails
     */
    public SkillsMetadataResult getMetadata() throws AgentBayException {
        return getMetadata(null, null);
    }

    /**
     * Get skills metadata with optional filtering.
     *
     * @param imageId    Image ID to determine the skills root path (optional)
     * @param skillNames Filter by skill names (optional)
     * @return SkillsMetadataResult with skills list and skillsRootPath
     * @throws AgentBayException if the API call fails
     */
    public SkillsMetadataResult getMetadata(String imageId, List<String> skillNames) throws AgentBayException {
        int maxAttempts = 3;
        int delayMs = 200;
        Exception lastException = null;

        for (int attempt = 1; attempt <= maxAttempts; attempt++) {
            try {
                GetSkillMetaDataRequest request = new GetSkillMetaDataRequest();
                request.setAuthorization("Bearer " + agentBay.getApiKey());
                if (imageId != null && !imageId.isEmpty()) {
                    request.setImageId(imageId);
                }
                if (skillNames != null && !skillNames.isEmpty()) {
                    request.setSkillGroupIds(skillNames);
                }

                GetSkillMetaDataResponse response = agentBay.getClient().getSkillMetaData(request);
                return parseGetSkillMetaDataResponse(response);
            } catch (Exception e) {
                lastException = e;
                String msg = e.getMessage() != null ? e.getMessage() : "";
                if (attempt < maxAttempts && (msg.contains("ServiceUnavailable") || msg.contains("503"))) {
                    try {
                        Thread.sleep(delayMs);
                    } catch (InterruptedException ie) {
                        Thread.currentThread().interrupt();
                        throw new AgentBayException("GetSkillMetaData interrupted: " + ie.getMessage(), ie);
                    }
                    delayMs *= 2;
                    continue;
                }
                break;
            }
        }

        if (lastException instanceof AgentBayException) {
            throw (AgentBayException) lastException;
        }
        throw new AgentBayException("GetSkillMetaData failed: " + (lastException != null ? lastException.getMessage() : "Unknown error"), lastException);
    }

    /**
     * Parse GetSkillMetaDataResponse into SkillsMetadataResult.
     * Exported for unit testing.
     */
    public static SkillsMetadataResult parseGetSkillMetaDataResponse(GetSkillMetaDataResponse response) throws AgentBayException {
        if (response == null || response.getBody() == null) {
            throw new AgentBayException("GetSkillMetaData failed: missing response body");
        }

        GetSkillMetaDataResponseBody body = response.getBody();
        if (body.getSuccess() == null || !body.getSuccess()) {
            String msg = body.getMessage() != null ? body.getMessage() : "Unknown error";
            String code = body.getCode() != null ? body.getCode() : "";
            if (!code.isEmpty()) {
                throw new AgentBayException("GetSkillMetaData failed: [" + code + "] " + msg);
            }
            throw new AgentBayException("GetSkillMetaData failed: " + msg);
        }

        GetSkillMetaDataResponseBody.GetSkillMetaDataResponseBodyData data = body.getData();
        if (data == null) {
            throw new AgentBayException("GetSkillMetaData failed: missing Data field");
        }

        String skillPath = data.getSkillPath() != null ? data.getSkillPath() : "";
        List<SkillMetadata> items = new ArrayList<>();
        if (data.getMetaDataList() != null) {
            for (GetSkillMetaDataResponseBody.GetSkillMetaDataResponseBodyDataMetaDataList raw : data.getMetaDataList()) {
                if (raw == null) {
                    continue;
                }
                String name = raw.getName() != null ? raw.getName().trim() : "";
                if (name.isEmpty()) {
                    continue;
                }
                String desc = raw.getDescription() != null ? raw.getDescription() : "";
                items.add(new SkillMetadata(name, desc));
            }
        }

        return new SkillsMetadataResult(items, skillPath);
    }

    /**
     * List official skills metadata via ListSkillMetaData.
     *
     * @deprecated Use getMetadata() instead, which returns both skills and skillsRootPath.
     */
    @Deprecated
    public List<SkillMetadata> listMetadata() throws AgentBayException {
        try {
            ListSkillMetaDataRequest request = new ListSkillMetaDataRequest();
            request.setAuthorization("Bearer " + agentBay.getApiKey());

            ListSkillMetaDataResponse response = agentBay.getClient().listSkillMetaData(request);
            if (response == null || response.getBody() == null) {
                throw new AgentBayException("ListSkillMetaData failed: missing response body");
            }

            ListSkillMetaDataResponseBody body = response.getBody();
            if (body.getSuccess() == null || !body.getSuccess()) {
                String msg = body.getMessage() != null ? body.getMessage() : "Unknown error";
                String code = body.getCode() != null ? body.getCode() : "";
                if (!code.isEmpty()) {
                    throw new AgentBayException("ListSkillMetaData failed: [" + code + "] " + msg);
                }
                throw new AgentBayException("ListSkillMetaData failed: " + msg);
            }

            List<ListSkillMetaDataResponseBody.ListSkillMetaDataResponseBodyData> data = body.getData();
            if (data == null) {
                throw new AgentBayException("ListSkillMetaData failed: invalid Data field");
            }

            List<SkillMetadata> items = new ArrayList<>();
            for (ListSkillMetaDataResponseBody.ListSkillMetaDataResponseBodyData raw : data) {
                if (raw == null) {
                    continue;
                }
                String name = raw.getName() != null ? raw.getName().trim() : "";
                if (name.isEmpty()) {
                    continue;
                }
                String desc = raw.getDescription() != null ? raw.getDescription() : "";
                items.add(new SkillMetadata(name, desc));
            }
            return items;
        } catch (AgentBayException e) {
            throw e;
        } catch (Exception e) {
            throw new AgentBayException("ListSkillMetaData failed: " + e.getMessage(), e);
        }
    }
}
