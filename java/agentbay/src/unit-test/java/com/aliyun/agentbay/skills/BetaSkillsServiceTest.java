package com.aliyun.agentbay.skills;

import com.aliyun.wuyingai20250506.models.GetSkillMetaDataResponse;
import com.aliyun.wuyingai20250506.models.GetSkillMetaDataResponseBody;
import org.junit.Test;

import java.util.ArrayList;
import java.util.List;

import static org.junit.Assert.*;

/**
 * Unit tests for BetaSkillsService.
 */
public class BetaSkillsServiceTest {

    @Test
    public void testParseGetSkillMetaDataResponse_Success() throws Exception {
        GetSkillMetaDataResponseBody.GetSkillMetaDataResponseBodyDataMetaDataList item1 =
            new GetSkillMetaDataResponseBody.GetSkillMetaDataResponseBodyDataMetaDataList();
        item1.setName("pdf");
        item1.setDescription("PDF processing skill");

        GetSkillMetaDataResponseBody.GetSkillMetaDataResponseBodyDataMetaDataList item2 =
            new GetSkillMetaDataResponseBody.GetSkillMetaDataResponseBodyDataMetaDataList();
        item2.setName("docx");
        item2.setDescription("Word document skill");

        List<GetSkillMetaDataResponseBody.GetSkillMetaDataResponseBodyDataMetaDataList> metaDataList = new ArrayList<>();
        metaDataList.add(item1);
        metaDataList.add(item2);

        GetSkillMetaDataResponseBody.GetSkillMetaDataResponseBodyData data =
            new GetSkillMetaDataResponseBody.GetSkillMetaDataResponseBodyData();
        data.setSkillPath("/home/wuying/skills");
        data.setMetaDataList(metaDataList);

        GetSkillMetaDataResponseBody body = new GetSkillMetaDataResponseBody();
        body.setSuccess(true);
        body.setData(data);

        GetSkillMetaDataResponse response = new GetSkillMetaDataResponse();
        response.setBody(body);

        SkillsMetadataResult result = BetaSkillsService.parseGetSkillMetaDataResponse(response);

        assertNotNull(result);
        assertEquals("/home/wuying/skills", result.getSkillsRootPath());
        assertEquals(2, result.getSkills().size());
        assertEquals("pdf", result.getSkills().get(0).getName());
        assertEquals("PDF processing skill", result.getSkills().get(0).getDescription());
        assertEquals("docx", result.getSkills().get(1).getName());
        assertEquals("Word document skill", result.getSkills().get(1).getDescription());
    }

    @Test
    public void testParseGetSkillMetaDataResponse_APIFailure() {
        GetSkillMetaDataResponseBody body = new GetSkillMetaDataResponseBody();
        body.setSuccess(false);
        body.setCode("InvalidRequest");
        body.setMessage("Bad group id");

        GetSkillMetaDataResponse response = new GetSkillMetaDataResponse();
        response.setBody(body);

        try {
            BetaSkillsService.parseGetSkillMetaDataResponse(response);
            fail("Expected AgentBayException");
        } catch (com.aliyun.agentbay.exception.AgentBayException e) {
            assertTrue(e.getMessage().contains("GetSkillMetaData failed"));
            assertTrue(e.getMessage().contains("InvalidRequest"));
            assertTrue(e.getMessage().contains("Bad group id"));
        }
    }

    @Test
    public void testParseGetSkillMetaDataResponse_SkipsEmptyNames() throws Exception {
        GetSkillMetaDataResponseBody.GetSkillMetaDataResponseBodyDataMetaDataList item1 =
            new GetSkillMetaDataResponseBody.GetSkillMetaDataResponseBodyDataMetaDataList();
        item1.setName("");
        item1.setDescription("Should be skipped");

        GetSkillMetaDataResponseBody.GetSkillMetaDataResponseBodyDataMetaDataList item2 =
            new GetSkillMetaDataResponseBody.GetSkillMetaDataResponseBodyDataMetaDataList();
        item2.setName("valid-skill");
        item2.setDescription("Valid");

        List<GetSkillMetaDataResponseBody.GetSkillMetaDataResponseBodyDataMetaDataList> metaDataList = new ArrayList<>();
        metaDataList.add(item1);
        metaDataList.add(item2);

        GetSkillMetaDataResponseBody.GetSkillMetaDataResponseBodyData data =
            new GetSkillMetaDataResponseBody.GetSkillMetaDataResponseBodyData();
        data.setSkillPath("/skills");
        data.setMetaDataList(metaDataList);

        GetSkillMetaDataResponseBody body = new GetSkillMetaDataResponseBody();
        body.setSuccess(true);
        body.setData(data);

        GetSkillMetaDataResponse response = new GetSkillMetaDataResponse();
        response.setBody(body);

        SkillsMetadataResult result = BetaSkillsService.parseGetSkillMetaDataResponse(response);

        assertNotNull(result);
        assertEquals(1, result.getSkills().size());
        assertEquals("valid-skill", result.getSkills().get(0).getName());
        assertEquals("Valid", result.getSkills().get(0).getDescription());
    }

    @Test
    public void testParseGetSkillMetaDataResponse_NilBody() {
        try {
            BetaSkillsService.parseGetSkillMetaDataResponse(null);
            fail("Expected AgentBayException");
        } catch (com.aliyun.agentbay.exception.AgentBayException e) {
            assertTrue(e.getMessage().contains("missing response body"));
        }
    }

    @Test
    public void testParseGetSkillMetaDataResponse_NilBodyObject() {
        GetSkillMetaDataResponse response = new GetSkillMetaDataResponse();
        response.setBody(null);

        try {
            BetaSkillsService.parseGetSkillMetaDataResponse(response);
            fail("Expected AgentBayException");
        } catch (com.aliyun.agentbay.exception.AgentBayException e) {
            assertTrue(e.getMessage().contains("missing response body"));
        }
    }

    @Test
    public void testParseGetSkillMetaDataResponse_NilData() {
        GetSkillMetaDataResponseBody body = new GetSkillMetaDataResponseBody();
        body.setSuccess(true);
        body.setData(null);

        GetSkillMetaDataResponse response = new GetSkillMetaDataResponse();
        response.setBody(body);

        try {
            BetaSkillsService.parseGetSkillMetaDataResponse(response);
            fail("Expected AgentBayException");
        } catch (com.aliyun.agentbay.exception.AgentBayException e) {
            assertTrue(e.getMessage().contains("missing Data field"));
        }
    }

    @Test
    public void testParseGetSkillMetaDataResponse_EmptyMetaDataList() throws Exception {
        GetSkillMetaDataResponseBody.GetSkillMetaDataResponseBodyData data =
            new GetSkillMetaDataResponseBody.GetSkillMetaDataResponseBodyData();
        data.setSkillPath("/skills");
        data.setMetaDataList(null);

        GetSkillMetaDataResponseBody body = new GetSkillMetaDataResponseBody();
        body.setSuccess(true);
        body.setData(data);

        GetSkillMetaDataResponse response = new GetSkillMetaDataResponse();
        response.setBody(body);

        SkillsMetadataResult result = BetaSkillsService.parseGetSkillMetaDataResponse(response);

        assertNotNull(result);
        assertEquals(0, result.getSkills().size());
        assertEquals("/skills", result.getSkillsRootPath());
    }
}
