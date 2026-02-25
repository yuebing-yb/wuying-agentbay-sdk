package com.aliyun.agentbay.skills;

import com.aliyun.agentbay.AgentBay;
import com.aliyun.agentbay.exception.AgentBayException;
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

