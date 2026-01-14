// This file is auto-generated, don't edit it. Thanks.
package com.aliyun.wuyingai20250506.models;

import com.aliyun.tea.*;

public class GetVolumeRequest extends TeaModel {
    @NameInMap("AllowCreate")
    public Boolean allowCreate;

    @NameInMap("Authorization")
    public String authorization;

    @NameInMap("ImageId")
    public String imageId;

    @NameInMap("VolumeName")
    public String volumeName;

    public static GetVolumeRequest build(java.util.Map<String, ?> map) throws Exception {
        GetVolumeRequest self = new GetVolumeRequest();
        return TeaModel.build(map, self);
    }

    public GetVolumeRequest setAllowCreate(Boolean allowCreate) {
        this.allowCreate = allowCreate;
        return this;
    }
    public Boolean getAllowCreate() {
        return this.allowCreate;
    }

    public GetVolumeRequest setAuthorization(String authorization) {
        this.authorization = authorization;
        return this;
    }
    public String getAuthorization() {
        return this.authorization;
    }

    public GetVolumeRequest setImageId(String imageId) {
        this.imageId = imageId;
        return this;
    }
    public String getImageId() {
        return this.imageId;
    }

    public GetVolumeRequest setVolumeName(String volumeName) {
        this.volumeName = volumeName;
        return this;
    }
    public String getVolumeName() {
        return this.volumeName;
    }

}
