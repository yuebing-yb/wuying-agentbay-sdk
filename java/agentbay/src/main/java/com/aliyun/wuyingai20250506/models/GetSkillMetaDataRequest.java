// This file is auto-generated, don't edit it. Thanks.
package com.aliyun.wuyingai20250506.models;

import com.aliyun.tea.*;

public class GetSkillMetaDataRequest extends TeaModel {
    @NameInMap("Authorization")
    public String authorization;

    @NameInMap("ImageId")
    public String imageId;

    @NameInMap("SkillGroupIds")
    public java.util.List<String> skillGroupIds;

    public static GetSkillMetaDataRequest build(java.util.Map<String, ?> map) throws Exception {
        GetSkillMetaDataRequest self = new GetSkillMetaDataRequest();
        return TeaModel.build(map, self);
    }

    public GetSkillMetaDataRequest setAuthorization(String authorization) {
        this.authorization = authorization;
        return this;
    }
    public String getAuthorization() {
        return this.authorization;
    }

    public GetSkillMetaDataRequest setImageId(String imageId) {
        this.imageId = imageId;
        return this;
    }
    public String getImageId() {
        return this.imageId;
    }

    public GetSkillMetaDataRequest setSkillGroupIds(java.util.List<String> skillGroupIds) {
        this.skillGroupIds = skillGroupIds;
        return this;
    }
    public java.util.List<String> getSkillGroupIds() {
        return this.skillGroupIds;
    }

}
