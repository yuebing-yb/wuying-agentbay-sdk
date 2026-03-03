// This file is auto-generated, don't edit it. Thanks.
package com.aliyun.wuyingai20250506.models;

import com.aliyun.tea.*;

public class ApplyMqttTokenResponseBody extends TeaModel {
    @NameInMap("Code")
    public String code;

    @NameInMap("Data")
    public ApplyMqttTokenResponseBodyData data;

    @NameInMap("HttpStatusCode")
    public Integer httpStatusCode;

    @NameInMap("Message")
    public String message;

    @NameInMap("RequestId")
    public String requestId;

    @NameInMap("Success")
    public Boolean success;

    public static ApplyMqttTokenResponseBody build(java.util.Map<String, ?> map) throws Exception {
        ApplyMqttTokenResponseBody self = new ApplyMqttTokenResponseBody();
        return TeaModel.build(map, self);
    }

    public ApplyMqttTokenResponseBody setCode(String code) {
        this.code = code;
        return this;
    }
    public String getCode() {
        return this.code;
    }

    public ApplyMqttTokenResponseBody setData(ApplyMqttTokenResponseBodyData data) {
        this.data = data;
        return this;
    }
    public ApplyMqttTokenResponseBodyData getData() {
        return this.data;
    }

    public ApplyMqttTokenResponseBody setHttpStatusCode(Integer httpStatusCode) {
        this.httpStatusCode = httpStatusCode;
        return this;
    }
    public Integer getHttpStatusCode() {
        return this.httpStatusCode;
    }

    public ApplyMqttTokenResponseBody setMessage(String message) {
        this.message = message;
        return this;
    }
    public String getMessage() {
        return this.message;
    }

    public ApplyMqttTokenResponseBody setRequestId(String requestId) {
        this.requestId = requestId;
        return this;
    }
    public String getRequestId() {
        return this.requestId;
    }

    public ApplyMqttTokenResponseBody setSuccess(Boolean success) {
        this.success = success;
        return this;
    }
    public Boolean getSuccess() {
        return this.success;
    }

    public static class ApplyMqttTokenResponseBodyData extends TeaModel {
        @NameInMap("AccessKeyId")
        public String accessKeyId;

        @NameInMap("ClientId")
        public String clientId;

        @NameInMap("Expiration")
        public String expiration;

        @NameInMap("InstanceId")
        public String instanceId;

        @NameInMap("RegionId")
        public String regionId;

        @NameInMap("SecurityToken")
        public String securityToken;

        public static ApplyMqttTokenResponseBodyData build(java.util.Map<String, ?> map) throws Exception {
            ApplyMqttTokenResponseBodyData self = new ApplyMqttTokenResponseBodyData();
            return TeaModel.build(map, self);
        }

        public ApplyMqttTokenResponseBodyData setAccessKeyId(String accessKeyId) {
            this.accessKeyId = accessKeyId;
            return this;
        }
        public String getAccessKeyId() {
            return this.accessKeyId;
        }

        public ApplyMqttTokenResponseBodyData setClientId(String clientId) {
            this.clientId = clientId;
            return this;
        }
        public String getClientId() {
            return this.clientId;
        }

        public ApplyMqttTokenResponseBodyData setExpiration(String expiration) {
            this.expiration = expiration;
            return this;
        }
        public String getExpiration() {
            return this.expiration;
        }

        public ApplyMqttTokenResponseBodyData setInstanceId(String instanceId) {
            this.instanceId = instanceId;
            return this;
        }
        public String getInstanceId() {
            return this.instanceId;
        }

        public ApplyMqttTokenResponseBodyData setRegionId(String regionId) {
            this.regionId = regionId;
            return this;
        }
        public String getRegionId() {
            return this.regionId;
        }

        public ApplyMqttTokenResponseBodyData setSecurityToken(String securityToken) {
            this.securityToken = securityToken;
            return this;
        }
        public String getSecurityToken() {
            return this.securityToken;
        }

    }

}
