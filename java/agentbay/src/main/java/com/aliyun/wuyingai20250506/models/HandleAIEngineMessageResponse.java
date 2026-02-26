// This file is auto-generated, don't edit it. Thanks.
package com.aliyun.wuyingai20250506.models;

import com.aliyun.tea.*;

public class HandleAIEngineMessageResponse extends TeaModel {
    @NameInMap("headers")
    public java.util.Map<String, String> headers;

    @NameInMap("statusCode")
    public Integer statusCode;

    @NameInMap("body")
    public HandleAIEngineMessageResponseBody body;

    public static HandleAIEngineMessageResponse build(java.util.Map<String, ?> map) throws Exception {
        HandleAIEngineMessageResponse self = new HandleAIEngineMessageResponse();
        return TeaModel.build(map, self);
    }

    public HandleAIEngineMessageResponse setHeaders(java.util.Map<String, String> headers) {
        this.headers = headers;
        return this;
    }
    public java.util.Map<String, String> getHeaders() {
        return this.headers;
    }

    public HandleAIEngineMessageResponse setStatusCode(Integer statusCode) {
        this.statusCode = statusCode;
        return this;
    }
    public Integer getStatusCode() {
        return this.statusCode;
    }

    public HandleAIEngineMessageResponse setBody(HandleAIEngineMessageResponseBody body) {
        this.body = body;
        return this;
    }
    public HandleAIEngineMessageResponseBody getBody() {
        return this.body;
    }

}
