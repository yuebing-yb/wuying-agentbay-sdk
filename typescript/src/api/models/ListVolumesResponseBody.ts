// This file is auto-generated, don't edit it
import * as $dara from '@darabonba/typescript';


export class ListVolumesResponseBodyData extends $dara.Model {
  belongingImageId?: string;
  createTime?: string;
  status?: string;
  volumeId?: string;
  volumeName?: string;
  static names(): { [key: string]: string } {
    return {
      belongingImageId: 'BelongingImageId',
      createTime: 'CreateTime',
      status: 'Status',
      volumeId: 'VolumeId',
      volumeName: 'VolumeName',
    };
  }

  static types(): { [key: string]: any } {
    return {
      belongingImageId: 'string',
      createTime: 'string',
      status: 'string',
      volumeId: 'string',
      volumeName: 'string',
    };
  }

  validate() {
    super.validate();
  }

  constructor(map?: { [key: string]: any }) {
    super(map);
  }
}

export class ListVolumesResponseBody extends $dara.Model {
  code?: string;
  data?: ListVolumesResponseBodyData[];
  httpStatusCode?: number;
  maxResults?: number;
  message?: string;
  nextToken?: string;
  requestId?: string;
  success?: boolean;
  static names(): { [key: string]: string } {
    return {
      code: 'Code',
      data: 'Data',
      httpStatusCode: 'HttpStatusCode',
      maxResults: 'MaxResults',
      message: 'Message',
      nextToken: 'NextToken',
      requestId: 'RequestId',
      success: 'Success',
    };
  }

  static types(): { [key: string]: any } {
    return {
      code: 'string',
      data: { 'type': 'array', 'itemType': ListVolumesResponseBodyData },
      httpStatusCode: 'number',
      maxResults: 'number',
      message: 'string',
      nextToken: 'string',
      requestId: 'string',
      success: 'boolean',
    };
  }

  validate() {
    if(Array.isArray(this.data)) {
      $dara.Model.validateArray(this.data);
    }
    super.validate();
  }

  constructor(map?: { [key: string]: any }) {
    super(map);
  }
}

