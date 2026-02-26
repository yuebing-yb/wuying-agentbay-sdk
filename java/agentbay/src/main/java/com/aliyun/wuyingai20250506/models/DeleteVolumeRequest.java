// This file is auto-generated, don't edit it. Thanks.
package com.aliyun.wuyingai20250506.models;

import com.aliyun.tea.*;

public class DeleteVolumeRequest extends TeaModel {
    @NameInMap("Authorization")
    public String authorization;

    /**
     * <p>This parameter is required.</p>
     */
    @NameInMap("VolumeId")
    public String volumeId;

    public static DeleteVolumeRequest build(java.util.Map<String, ?> map) throws Exception {
        DeleteVolumeRequest self = new DeleteVolumeRequest();
        return TeaModel.build(map, self);
    }

    public DeleteVolumeRequest setAuthorization(String authorization) {
        this.authorization = authorization;
        return this;
    }
    public String getAuthorization() {
        return this.authorization;
    }

    public DeleteVolumeRequest setVolumeId(String volumeId) {
        this.volumeId = volumeId;
        return this;
    }
    public String getVolumeId() {
        return this.volumeId;
    }

}
