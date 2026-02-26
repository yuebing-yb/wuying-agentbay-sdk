// This file is auto-generated, don't edit it. Thanks.
package com.aliyun.wuyingai20250506.models;

import com.aliyun.tea.*;

public class ListVolumesResponseBody extends TeaModel {
    @NameInMap("Code")
    public String code;

    @NameInMap("Data")
    public java.util.List<ListVolumesResponseBodyData> data;

    @NameInMap("HttpStatusCode")
    public Integer httpStatusCode;

    @NameInMap("MaxResults")
    public Integer maxResults;

    @NameInMap("Message")
    public String message;

    @NameInMap("NextToken")
    public String nextToken;

    @NameInMap("RequestId")
    public String requestId;

    @NameInMap("Success")
    public Boolean success;

    public static ListVolumesResponseBody build(java.util.Map<String, ?> map) throws Exception {
        ListVolumesResponseBody self = new ListVolumesResponseBody();
        return TeaModel.build(map, self);
    }

    public ListVolumesResponseBody setCode(String code) {
        this.code = code;
        return this;
    }
    public String getCode() {
        return this.code;
    }

    public ListVolumesResponseBody setData(java.util.List<ListVolumesResponseBodyData> data) {
        this.data = data;
        return this;
    }
    public java.util.List<ListVolumesResponseBodyData> getData() {
        return this.data;
    }

    public ListVolumesResponseBody setHttpStatusCode(Integer httpStatusCode) {
        this.httpStatusCode = httpStatusCode;
        return this;
    }
    public Integer getHttpStatusCode() {
        return this.httpStatusCode;
    }

    public ListVolumesResponseBody setMaxResults(Integer maxResults) {
        this.maxResults = maxResults;
        return this;
    }
    public Integer getMaxResults() {
        return this.maxResults;
    }

    public ListVolumesResponseBody setMessage(String message) {
        this.message = message;
        return this;
    }
    public String getMessage() {
        return this.message;
    }

    public ListVolumesResponseBody setNextToken(String nextToken) {
        this.nextToken = nextToken;
        return this;
    }
    public String getNextToken() {
        return this.nextToken;
    }

    public ListVolumesResponseBody setRequestId(String requestId) {
        this.requestId = requestId;
        return this;
    }
    public String getRequestId() {
        return this.requestId;
    }

    public ListVolumesResponseBody setSuccess(Boolean success) {
        this.success = success;
        return this;
    }
    public Boolean getSuccess() {
        return this.success;
    }

    public static class ListVolumesResponseBodyData extends TeaModel {
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

        public static ListVolumesResponseBodyData build(java.util.Map<String, ?> map) throws Exception {
            ListVolumesResponseBodyData self = new ListVolumesResponseBodyData();
            return TeaModel.build(map, self);
        }

        public ListVolumesResponseBodyData setBelongingImageId(String belongingImageId) {
            this.belongingImageId = belongingImageId;
            return this;
        }
        public String getBelongingImageId() {
            return this.belongingImageId;
        }

        public ListVolumesResponseBodyData setCreateTime(String createTime) {
            this.createTime = createTime;
            return this;
        }
        public String getCreateTime() {
            return this.createTime;
        }

        public ListVolumesResponseBodyData setStatus(String status) {
            this.status = status;
            return this;
        }
        public String getStatus() {
            return this.status;
        }

        public ListVolumesResponseBodyData setVolumeId(String volumeId) {
            this.volumeId = volumeId;
            return this;
        }
        public String getVolumeId() {
            return this.volumeId;
        }

        public ListVolumesResponseBodyData setVolumeName(String volumeName) {
            this.volumeName = volumeName;
            return this;
        }
        public String getVolumeName() {
            return this.volumeName;
        }

    }

}
