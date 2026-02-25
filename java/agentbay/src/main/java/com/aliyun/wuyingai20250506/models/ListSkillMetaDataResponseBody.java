// This file is auto-generated, don't edit it. Thanks.
package com.aliyun.wuyingai20250506.models;

import com.aliyun.tea.*;

import java.util.List;

public class ListSkillMetaDataResponseBody extends TeaModel {
    @NameInMap("Code")
    public String code;

    @NameInMap("Data")
    public List<ListSkillMetaDataResponseBodyData> data;

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

    public static ListSkillMetaDataResponseBody build(java.util.Map<String, ?> map) throws Exception {
        ListSkillMetaDataResponseBody self = new ListSkillMetaDataResponseBody();
        return TeaModel.build(map, self);
    }

    public ListSkillMetaDataResponseBody setCode(String code) {
        this.code = code;
        return this;
    }

    public String getCode() {
        return this.code;
    }

    public ListSkillMetaDataResponseBody setData(List<ListSkillMetaDataResponseBodyData> data) {
        this.data = data;
        return this;
    }

    public List<ListSkillMetaDataResponseBodyData> getData() {
        return this.data;
    }

    public ListSkillMetaDataResponseBody setHttpStatusCode(Integer httpStatusCode) {
        this.httpStatusCode = httpStatusCode;
        return this;
    }

    public Integer getHttpStatusCode() {
        return this.httpStatusCode;
    }

    public ListSkillMetaDataResponseBody setMessage(String message) {
        this.message = message;
        return this;
    }

    public String getMessage() {
        return this.message;
    }

    public ListSkillMetaDataResponseBody setRequestId(String requestId) {
        this.requestId = requestId;
        return this;
    }

    public String getRequestId() {
        return this.requestId;
    }

    public ListSkillMetaDataResponseBody setSuccess(Boolean success) {
        this.success = success;
        return this;
    }

    public Boolean getSuccess() {
        return this.success;
    }

    public ListSkillMetaDataResponseBody setTotalCount(Integer totalCount) {
        this.totalCount = totalCount;
        return this;
    }

    public Integer getTotalCount() {
        return this.totalCount;
    }

    public static class ListSkillMetaDataResponseBodyData extends TeaModel {
        @NameInMap("Description")
        public String description;

        @NameInMap("Name")
        public String name;

        public static ListSkillMetaDataResponseBodyData build(java.util.Map<String, ?> map) throws Exception {
            ListSkillMetaDataResponseBodyData self = new ListSkillMetaDataResponseBodyData();
            return TeaModel.build(map, self);
        }

        public ListSkillMetaDataResponseBodyData setDescription(String description) {
            this.description = description;
            return this;
        }

        public String getDescription() {
            return this.description;
        }

        public ListSkillMetaDataResponseBodyData setName(String name) {
            this.name = name;
            return this;
        }

        public String getName() {
            return this.name;
        }
    }
}

