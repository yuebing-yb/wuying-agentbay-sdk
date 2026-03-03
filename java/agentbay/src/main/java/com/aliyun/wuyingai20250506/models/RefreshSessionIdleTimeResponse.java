// This file is auto-generated, don't edit it. Thanks.
package com.aliyun.wuyingai20250506.models;

import com.aliyun.tea.*;

public class RefreshSessionIdleTimeResponse extends TeaModel {
    @NameInMap("headers")
    public java.util.Map<String, String> headers;

    @NameInMap("statusCode")
    public Integer statusCode;

    @NameInMap("body")
    public RefreshSessionIdleTimeResponseBody body;

    public static RefreshSessionIdleTimeResponse build(java.util.Map<String, ?> map) throws Exception {
        RefreshSessionIdleTimeResponse self = new RefreshSessionIdleTimeResponse();
        return TeaModel.build(map, self);
    }

    public RefreshSessionIdleTimeResponse setHeaders(java.util.Map<String, String> headers) {
        this.headers = headers;
        return this;
    }
    public java.util.Map<String, String> getHeaders() {
        return this.headers;
    }

    public RefreshSessionIdleTimeResponse setStatusCode(Integer statusCode) {
        this.statusCode = statusCode;
        return this;
    }
    public Integer getStatusCode() {
        return this.statusCode;
    }

    public RefreshSessionIdleTimeResponse setBody(RefreshSessionIdleTimeResponseBody body) {
        this.body = body;
        return this;
    }
    public RefreshSessionIdleTimeResponseBody getBody() {
        return this.body;
    }

}
