// This file is auto-generated, don't edit it. Thanks.
package com.aliyun.wuyingai20250506.models;

import com.aliyun.tea.*;

public class GetSkillMetaDataResponse extends TeaModel {
    @NameInMap("headers")
    public java.util.Map<String, String> headers;

    @NameInMap("statusCode")
    public Integer statusCode;

    @NameInMap("body")
    public GetSkillMetaDataResponseBody body;

    public static GetSkillMetaDataResponse build(java.util.Map<String, ?> map) throws Exception {
        GetSkillMetaDataResponse self = new GetSkillMetaDataResponse();
        return TeaModel.build(map, self);
    }

    public GetSkillMetaDataResponse setHeaders(java.util.Map<String, String> headers) {
        this.headers = headers;
        return this;
    }
    public java.util.Map<String, String> getHeaders() {
        return this.headers;
    }

    public GetSkillMetaDataResponse setStatusCode(Integer statusCode) {
        this.statusCode = statusCode;
        return this;
    }
    public Integer getStatusCode() {
        return this.statusCode;
    }

    public GetSkillMetaDataResponse setBody(GetSkillMetaDataResponseBody body) {
        this.body = body;
        return this;
    }
    public GetSkillMetaDataResponseBody getBody() {
        return this.body;
    }

}
