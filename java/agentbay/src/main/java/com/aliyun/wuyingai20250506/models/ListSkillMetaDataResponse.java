// This file is auto-generated, don't edit it. Thanks.
package com.aliyun.wuyingai20250506.models;

import com.aliyun.tea.*;

public class ListSkillMetaDataResponse extends TeaModel {
    @NameInMap("headers")
    public java.util.Map<String, String> headers;

    @NameInMap("statusCode")
    public Integer statusCode;

    @NameInMap("body")
    public ListSkillMetaDataResponseBody body;

    public static ListSkillMetaDataResponse build(java.util.Map<String, ?> map) throws Exception {
        ListSkillMetaDataResponse self = new ListSkillMetaDataResponse();
        return TeaModel.build(map, self);
    }

    public ListSkillMetaDataResponse setHeaders(java.util.Map<String, String> headers) {
        this.headers = headers;
        return this;
    }

    public java.util.Map<String, String> getHeaders() {
        return this.headers;
    }

    public ListSkillMetaDataResponse setStatusCode(Integer statusCode) {
        this.statusCode = statusCode;
        return this;
    }

    public Integer getStatusCode() {
        return this.statusCode;
    }

    public ListSkillMetaDataResponse setBody(ListSkillMetaDataResponseBody body) {
        this.body = body;
        return this;
    }

    public ListSkillMetaDataResponseBody getBody() {
        return this.body;
    }
}

