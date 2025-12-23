// This file is auto-generated, don't edit it
import * as $dara from "@darabonba/typescript";

export class GetSessionDetailResponseBodyData extends $dara.Model {
  aliuid?: string;
  apikeyId?: string;
  appInstanceGroupId?: string;
  appInstanceId?: string;
  appUserId?: string;
  bizType?: number;
  endReason?: string;
  id?: number;
  imageId?: string;
  imageType?: string;
  isDeleted?: number;
  policyId?: string;
  regionId?: string;
  resourceConfigId?: string;
  status?: string;
  static names(): { [key: string]: string } {
    return {
      aliuid: "Aliuid",
      apikeyId: "ApikeyId",
      appInstanceGroupId: "AppInstanceGroupId",
      appInstanceId: "AppInstanceId",
      appUserId: "AppUserId",
      bizType: "BizType",
      endReason: "EndReason",
      id: "Id",
      imageId: "ImageId",
      imageType: "ImageType",
      isDeleted: "IsDeleted",
      policyId: "PolicyId",
      regionId: "RegionId",
      resourceConfigId: "ResourceConfigId",
      status: "Status",
    };
  }

  static types(): { [key: string]: any } {
    return {
      aliuid: "string",
      apikeyId: "string",
      appInstanceGroupId: "string",
      appInstanceId: "string",
      appUserId: "string",
      bizType: "number",
      endReason: "string",
      id: "number",
      imageId: "string",
      imageType: "string",
      isDeleted: "number",
      policyId: "string",
      regionId: "string",
      resourceConfigId: "string",
      status: "string",
    };
  }

  validate() {
    super.validate();
  }

  constructor(map?: { [key: string]: any }) {
    super(map);
  }
}


