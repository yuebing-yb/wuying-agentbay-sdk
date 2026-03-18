// This file is auto-generated, don't edit it. Thanks.
package com.aliyun.wuyingai20250506.models;

import com.aliyun.tea.*;

public class GetSkillMetaDataResponseBody extends TeaModel {
    @NameInMap("Code")
    public String code;

    @NameInMap("Data")
    public GetSkillMetaDataResponseBodyData data;

    @NameInMap("HttpStatusCode")
    public Integer httpStatusCode;

    @NameInMap("Message")
    public String message;

    @NameInMap("RequestId")
    public String requestId;

    @NameInMap("Success")
    public Boolean success;

    @NameInMap("TotalCount")
    public Integer totalCount;

    public static GetSkillMetaDataResponseBody build(java.util.Map<String, ?> map) throws Exception {
        GetSkillMetaDataResponseBody self = new GetSkillMetaDataResponseBody();
        return TeaModel.build(map, self);
    }

    public GetSkillMetaDataResponseBody setCode(String code) {
        this.code = code;
        return this;
    }
    public String getCode() {
        return this.code;
    }

    public GetSkillMetaDataResponseBody setData(GetSkillMetaDataResponseBodyData data) {
        this.data = data;
        return this;
    }
    public GetSkillMetaDataResponseBodyData getData() {
        return this.data;
    }

    public GetSkillMetaDataResponseBody setHttpStatusCode(Integer httpStatusCode) {
        this.httpStatusCode = httpStatusCode;
        return this;
    }
    public Integer getHttpStatusCode() {
        return this.httpStatusCode;
    }

    public GetSkillMetaDataResponseBody setMessage(String message) {
        this.message = message;
        return this;
    }
    public String getMessage() {
        return this.message;
    }

    public GetSkillMetaDataResponseBody setRequestId(String requestId) {
        this.requestId = requestId;
        return this;
    }
    public String getRequestId() {
        return this.requestId;
    }

    public GetSkillMetaDataResponseBody setSuccess(Boolean success) {
        this.success = success;
        return this;
    }
    public Boolean getSuccess() {
        return this.success;
    }

    public GetSkillMetaDataResponseBody setTotalCount(Integer totalCount) {
        this.totalCount = totalCount;
        return this;
    }
    public Integer getTotalCount() {
        return this.totalCount;
    }

    public static class GetSkillMetaDataResponseBodyDataMetaDataList extends TeaModel {
        @NameInMap("Description")
        public String description;

        @NameInMap("Name")
        public String name;

        public static GetSkillMetaDataResponseBodyDataMetaDataList build(java.util.Map<String, ?> map) throws Exception {
            GetSkillMetaDataResponseBodyDataMetaDataList self = new GetSkillMetaDataResponseBodyDataMetaDataList();
            return TeaModel.build(map, self);
        }

        public GetSkillMetaDataResponseBodyDataMetaDataList setDescription(String description) {
            this.description = description;
            return this;
        }
        public String getDescription() {
            return this.description;
        }

        public GetSkillMetaDataResponseBodyDataMetaDataList setName(String name) {
            this.name = name;
            return this;
        }
        public String getName() {
            return this.name;
        }

    }

    public static class GetSkillMetaDataResponseBodyData extends TeaModel {
        @NameInMap("MetaDataList")
        public java.util.List<GetSkillMetaDataResponseBodyDataMetaDataList> metaDataList;

        @NameInMap("SkillPath")
        public String skillPath;

        public static GetSkillMetaDataResponseBodyData build(java.util.Map<String, ?> map) throws Exception {
            GetSkillMetaDataResponseBodyData self = new GetSkillMetaDataResponseBodyData();
            return TeaModel.build(map, self);
        }

        public GetSkillMetaDataResponseBodyData setMetaDataList(java.util.List<GetSkillMetaDataResponseBodyDataMetaDataList> metaDataList) {
            this.metaDataList = metaDataList;
            return this;
        }
        public java.util.List<GetSkillMetaDataResponseBodyDataMetaDataList> getMetaDataList() {
            return this.metaDataList;
        }

        public GetSkillMetaDataResponseBodyData setSkillPath(String skillPath) {
            this.skillPath = skillPath;
            return this;
        }
        public String getSkillPath() {
            return this.skillPath;
        }

    }

}
