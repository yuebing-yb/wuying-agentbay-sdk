// This file is auto-generated, don't edit it. Thanks.
package com.aliyun.wuyingai20250506.models;

import com.aliyun.tea.*;

public class HandleAIEngineMessageRequest extends TeaModel {
    @NameInMap("Data")
    public String data;

    @NameInMap("MsgType")
    public String msgType;

    @NameInMap("SessionToken")
    public String sessionToken;

    public static HandleAIEngineMessageRequest build(java.util.Map<String, ?> map) throws Exception {
        HandleAIEngineMessageRequest self = new HandleAIEngineMessageRequest();
        return TeaModel.build(map, self);
    }

    public HandleAIEngineMessageRequest setData(String data) {
        this.data = data;
        return this;
    }
    public String getData() {
        return this.data;
    }

    public HandleAIEngineMessageRequest setMsgType(String msgType) {
        this.msgType = msgType;
        return this;
    }
    public String getMsgType() {
        return this.msgType;
    }

    public HandleAIEngineMessageRequest setSessionToken(String sessionToken) {
        this.sessionToken = sessionToken;
        return this;
    }
    public String getSessionToken() {
        return this.sessionToken;
    }

}
