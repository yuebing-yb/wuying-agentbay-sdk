// This file is auto-generated, don't edit it. Thanks.
package com.aliyun.wuyingai20250506.models;

import com.aliyun.tea.*;

public class GetVolumeResponseBody extends TeaModel {
    @NameInMap("Code")
    public String code;

    @NameInMap("Data")
    public GetVolumeResponseBodyData data;

    @NameInMap("HttpStatusCode")
    public Integer httpStatusCode;

    @NameInMap("Message")
    public String message;

    @NameInMap("RequestId")
    public String requestId;

    @NameInMap("Success")
    public Boolean success;

    public static GetVolumeResponseBody build(java.util.Map<String, ?> map) throws Exception {
        GetVolumeResponseBody self = new GetVolumeResponseBody();
        return TeaModel.build(map, self);
    }

    public GetVolumeResponseBody setCode(String code) {
        this.code = code;
        return this;
    }
    public String getCode() {
        return this.code;
    }

    public GetVolumeResponseBody setData(GetVolumeResponseBodyData data) {
        this.data = data;
        return this;
    }
    public GetVolumeResponseBodyData getData() {
        return this.data;
    }

    public GetVolumeResponseBody setHttpStatusCode(Integer httpStatusCode) {
        this.httpStatusCode = httpStatusCode;
        return this;
    }
    public Integer getHttpStatusCode() {
        return this.httpStatusCode;
    }

    public GetVolumeResponseBody setMessage(String message) {
        this.message = message;
        return this;
    }
    public String getMessage() {
        return this.message;
    }

    public GetVolumeResponseBody setRequestId(String requestId) {
        this.requestId = requestId;
        return this;
    }
    public String getRequestId() {
        return this.requestId;
    }

    public GetVolumeResponseBody setSuccess(Boolean success) {
        this.success = success;
        return this;
    }
    public Boolean getSuccess() {
        return this.success;
    }

    public static class GetVolumeResponseBodyData extends TeaModel {
        @NameInMap("BelongingImageId")
        public String belongingImageId;

        @NameInMap("CreateTime")
        public String createTime;

        @NameInMap("Status")
        public String status;

        @NameInMap("VolumeId")
        public String volumeId;

        @NameInMap("VolumeName")
        public String volumeName;

        public static GetVolumeResponseBodyData build(java.util.Map<String, ?> map) throws Exception {
            GetVolumeResponseBodyData self = new GetVolumeResponseBodyData();
            return TeaModel.build(map, self);
        }

        public GetVolumeResponseBodyData setBelongingImageId(String belongingImageId) {
            this.belongingImageId = belongingImageId;
            return this;
        }
        public String getBelongingImageId() {
            return this.belongingImageId;
        }

        public GetVolumeResponseBodyData setCreateTime(String createTime) {
            this.createTime = createTime;
            return this;
        }
        public String getCreateTime() {
            return this.createTime;
        }

        public GetVolumeResponseBodyData setStatus(String status) {
            this.status = status;
            return this;
        }
        public String getStatus() {
            return this.status;
        }

        public GetVolumeResponseBodyData setVolumeId(String volumeId) {
            this.volumeId = volumeId;
            return this;
        }
        public String getVolumeId() {
            return this.volumeId;
        }

        public GetVolumeResponseBodyData setVolumeName(String volumeName) {
            this.volumeName = volumeName;
            return this;
        }
        public String getVolumeName() {
            return this.volumeName;
        }

    }

}
