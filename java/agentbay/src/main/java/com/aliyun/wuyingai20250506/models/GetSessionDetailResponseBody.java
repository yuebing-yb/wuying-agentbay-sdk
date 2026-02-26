// This file is auto-generated, don't edit it. Thanks.
package com.aliyun.wuyingai20250506.models;

import com.aliyun.tea.*;

public class GetSessionDetailResponseBody extends TeaModel {
    @NameInMap("Code")
    public String code;

    @NameInMap("Data")
    public GetSessionDetailResponseBodyData data;

    @NameInMap("HttpStatusCode")
    public Integer httpStatusCode;

    @NameInMap("Message")
    public String message;

    @NameInMap("RequestId")
    public String requestId;

    @NameInMap("Success")
    public Boolean success;

    public static GetSessionDetailResponseBody build(java.util.Map<String, ?> map) throws Exception {
        GetSessionDetailResponseBody self = new GetSessionDetailResponseBody();
        return TeaModel.build(map, self);
    }

    public GetSessionDetailResponseBody setCode(String code) {
        this.code = code;
        return this;
    }
    public String getCode() {
        return this.code;
    }

    public GetSessionDetailResponseBody setData(GetSessionDetailResponseBodyData data) {
        this.data = data;
        return this;
    }
    public GetSessionDetailResponseBodyData getData() {
        return this.data;
    }

    public GetSessionDetailResponseBody setHttpStatusCode(Integer httpStatusCode) {
        this.httpStatusCode = httpStatusCode;
        return this;
    }
    public Integer getHttpStatusCode() {
        return this.httpStatusCode;
    }

    public GetSessionDetailResponseBody setMessage(String message) {
        this.message = message;
        return this;
    }
    public String getMessage() {
        return this.message;
    }

    public GetSessionDetailResponseBody setRequestId(String requestId) {
        this.requestId = requestId;
        return this;
    }
    public String getRequestId() {
        return this.requestId;
    }

    public GetSessionDetailResponseBody setSuccess(Boolean success) {
        this.success = success;
        return this;
    }
    public Boolean getSuccess() {
        return this.success;
    }

    public static class GetSessionDetailResponseBodyData extends TeaModel {
        @NameInMap("Aliuid")
        public String aliuid;

        @NameInMap("ApikeyId")
        public String apikeyId;

        @NameInMap("AppInstanceGroupId")
        public String appInstanceGroupId;

        @NameInMap("AppInstanceId")
        public String appInstanceId;

        @NameInMap("AppUserId")
        public String appUserId;

        @NameInMap("BizType")
        public Integer bizType;

        @NameInMap("EndReason")
        public String endReason;

        @NameInMap("Id")
        public Long id;

        @NameInMap("ImageId")
        public String imageId;

        @NameInMap("ImageType")
        public String imageType;

        @NameInMap("IsDeleted")
        public Integer isDeleted;

        @NameInMap("PolicyId")
        public String policyId;

        @NameInMap("RegionId")
        public String regionId;

        @NameInMap("ResourceConfigId")
        public String resourceConfigId;

        @NameInMap("Status")
        public String status;

        public static GetSessionDetailResponseBodyData build(java.util.Map<String, ?> map) throws Exception {
            GetSessionDetailResponseBodyData self = new GetSessionDetailResponseBodyData();
            return TeaModel.build(map, self);
        }

        public GetSessionDetailResponseBodyData setAliuid(String aliuid) {
            this.aliuid = aliuid;
            return this;
        }
        public String getAliuid() {
            return this.aliuid;
        }

        public GetSessionDetailResponseBodyData setApikeyId(String apikeyId) {
            this.apikeyId = apikeyId;
            return this;
        }
        public String getApikeyId() {
            return this.apikeyId;
        }

        public GetSessionDetailResponseBodyData setAppInstanceGroupId(String appInstanceGroupId) {
            this.appInstanceGroupId = appInstanceGroupId;
            return this;
        }
        public String getAppInstanceGroupId() {
            return this.appInstanceGroupId;
        }

        public GetSessionDetailResponseBodyData setAppInstanceId(String appInstanceId) {
            this.appInstanceId = appInstanceId;
            return this;
        }
        public String getAppInstanceId() {
            return this.appInstanceId;
        }

        public GetSessionDetailResponseBodyData setAppUserId(String appUserId) {
            this.appUserId = appUserId;
            return this;
        }
        public String getAppUserId() {
            return this.appUserId;
        }

        public GetSessionDetailResponseBodyData setBizType(Integer bizType) {
            this.bizType = bizType;
            return this;
        }
        public Integer getBizType() {
            return this.bizType;
        }

        public GetSessionDetailResponseBodyData setEndReason(String endReason) {
            this.endReason = endReason;
            return this;
        }
        public String getEndReason() {
            return this.endReason;
        }

        public GetSessionDetailResponseBodyData setId(Long id) {
            this.id = id;
            return this;
        }
        public Long getId() {
            return this.id;
        }

        public GetSessionDetailResponseBodyData setImageId(String imageId) {
            this.imageId = imageId;
            return this;
        }
        public String getImageId() {
            return this.imageId;
        }

        public GetSessionDetailResponseBodyData setImageType(String imageType) {
            this.imageType = imageType;
            return this;
        }
        public String getImageType() {
            return this.imageType;
        }

        public GetSessionDetailResponseBodyData setIsDeleted(Integer isDeleted) {
            this.isDeleted = isDeleted;
            return this;
        }
        public Integer getIsDeleted() {
            return this.isDeleted;
        }

        public GetSessionDetailResponseBodyData setPolicyId(String policyId) {
            this.policyId = policyId;
            return this;
        }
        public String getPolicyId() {
            return this.policyId;
        }

        public GetSessionDetailResponseBodyData setRegionId(String regionId) {
            this.regionId = regionId;
            return this;
        }
        public String getRegionId() {
            return this.regionId;
        }

        public GetSessionDetailResponseBodyData setResourceConfigId(String resourceConfigId) {
            this.resourceConfigId = resourceConfigId;
            return this;
        }
        public String getResourceConfigId() {
            return this.resourceConfigId;
        }

        public GetSessionDetailResponseBodyData setStatus(String status) {
            this.status = status;
            return this;
        }
        public String getStatus() {
            return this.status;
        }

    }

}
