// This file is auto-generated, don't edit it. Thanks.
package com.aliyun.wuyingai20250506.models;

import com.aliyun.tea.*;

public class ApplyMqttTokenResponse extends TeaModel {
    @NameInMap("headers")
    public java.util.Map<String, String> headers;

    @NameInMap("statusCode")
    public Integer statusCode;

    @NameInMap("body")
    public ApplyMqttTokenResponseBody body;

    public static ApplyMqttTokenResponse build(java.util.Map<String, ?> map) throws Exception {
        ApplyMqttTokenResponse self = new ApplyMqttTokenResponse();
        return TeaModel.build(map, self);
    }

    public ApplyMqttTokenResponse setHeaders(java.util.Map<String, String> headers) {
        this.headers = headers;
        return this;
    }
    public java.util.Map<String, String> getHeaders() {
        return this.headers;
    }

    public ApplyMqttTokenResponse setStatusCode(Integer statusCode) {
        this.statusCode = statusCode;
        return this;
    }
    public Integer getStatusCode() {
        return this.statusCode;
    }

    public ApplyMqttTokenResponse setBody(ApplyMqttTokenResponseBody body) {
        this.body = body;
        return this;
    }
    public ApplyMqttTokenResponseBody getBody() {
        return this.body;
    }

}
