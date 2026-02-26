// This file is auto-generated, don't edit it. Thanks.
package com.aliyun.wuyingai20250506.models;

import com.aliyun.tea.*;

public class GetSessionDetailResponse extends TeaModel {
    @NameInMap("headers")
    public java.util.Map<String, String> headers;

    @NameInMap("statusCode")
    public Integer statusCode;

    @NameInMap("body")
    public GetSessionDetailResponseBody body;

    public static GetSessionDetailResponse build(java.util.Map<String, ?> map) throws Exception {
        GetSessionDetailResponse self = new GetSessionDetailResponse();
        return TeaModel.build(map, self);
    }

    public GetSessionDetailResponse setHeaders(java.util.Map<String, String> headers) {
        this.headers = headers;
        return this;
    }
    public java.util.Map<String, String> getHeaders() {
        return this.headers;
    }

    public GetSessionDetailResponse setStatusCode(Integer statusCode) {
        this.statusCode = statusCode;
        return this;
    }
    public Integer getStatusCode() {
        return this.statusCode;
    }

    public GetSessionDetailResponse setBody(GetSessionDetailResponseBody body) {
        this.body = body;
        return this;
    }
    public GetSessionDetailResponseBody getBody() {
        return this.body;
    }

}
