// This file is auto-generated, don't edit it. Thanks.
package com.aliyun.wuyingai20250506.models;

import com.aliyun.tea.*;

public class ListSkillMetaDataRequest extends TeaModel {
    @NameInMap("Authorization")
    public String authorization;

    public static ListSkillMetaDataRequest build(java.util.Map<String, ?> map) throws Exception {
        ListSkillMetaDataRequest self = new ListSkillMetaDataRequest();
        return TeaModel.build(map, self);
    }

    public ListSkillMetaDataRequest setAuthorization(String authorization) {
        this.authorization = authorization;
        return this;
    }
    public String getAuthorization() {
        return this.authorization;
    }

}
