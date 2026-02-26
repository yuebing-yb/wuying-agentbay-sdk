// This file is auto-generated, don't edit it. Thanks.
package com.aliyun.wuyingai20250506.models;

import com.aliyun.tea.*;

public class ApplyMqttTokenRequest extends TeaModel {
    @NameInMap("DesktopId")
    public String desktopId;

    @NameInMap("SessionToken")
    public String sessionToken;

    public static ApplyMqttTokenRequest build(java.util.Map<String, ?> map) throws Exception {
        ApplyMqttTokenRequest self = new ApplyMqttTokenRequest();
        return TeaModel.build(map, self);
    }

    public ApplyMqttTokenRequest setDesktopId(String desktopId) {
        this.desktopId = desktopId;
        return this;
    }
    public String getDesktopId() {
        return this.desktopId;
    }

    public ApplyMqttTokenRequest setSessionToken(String sessionToken) {
        this.sessionToken = sessionToken;
        return this;
    }
    public String getSessionToken() {
        return this.sessionToken;
    }

}
