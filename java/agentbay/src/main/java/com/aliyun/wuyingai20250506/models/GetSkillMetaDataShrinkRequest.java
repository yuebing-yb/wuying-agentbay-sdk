// This file is auto-generated, don't edit it. Thanks.
package com.aliyun.wuyingai20250506.models;

import com.aliyun.tea.*;

public class GetSkillMetaDataShrinkRequest extends TeaModel {
    @NameInMap("Authorization")
    public String authorization;

    @NameInMap("ImageId")
    public String imageId;

    @NameInMap("SkillGroupIds")
    public String skillGroupIdsShrink;

    public static GetSkillMetaDataShrinkRequest build(java.util.Map<String, ?> map) throws Exception {
        GetSkillMetaDataShrinkRequest self = new GetSkillMetaDataShrinkRequest();
        return TeaModel.build(map, self);
    }

    public GetSkillMetaDataShrinkRequest setAuthorization(String authorization) {
        this.authorization = authorization;
        return this;
    }
    public String getAuthorization() {
        return this.authorization;
    }

    public GetSkillMetaDataShrinkRequest setImageId(String imageId) {
        this.imageId = imageId;
        return this;
    }
    public String getImageId() {
        return this.imageId;
    }

    public GetSkillMetaDataShrinkRequest setSkillGroupIdsShrink(String skillGroupIdsShrink) {
        this.skillGroupIdsShrink = skillGroupIdsShrink;
        return this;
    }
    public String getSkillGroupIdsShrink() {
        return this.skillGroupIdsShrink;
    }

}
