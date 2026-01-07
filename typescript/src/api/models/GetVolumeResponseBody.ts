// This file is auto-generated, don't edit it
import * as $dara from '@darabonba/typescript';


export class GetVolumeResponseBodyData extends $dara.Model {
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

export class GetVolumeResponseBody extends $dara.Model {
  code?: string;
  data?: GetVolumeResponseBodyData;
  httpStatusCode?: number;
  message?: string;
  requestId?: string;
  success?: boolean;
  static names(): { [key: string]: string } {
    return {
      code: 'Code',
      data: 'Data',
      httpStatusCode: 'HttpStatusCode',
      message: 'Message',
      requestId: 'RequestId',
      success: 'Success',
    };
  }

  static types(): { [key: string]: any } {
    return {
      code: 'string',
      data: GetVolumeResponseBodyData,
      httpStatusCode: 'number',
      message: 'string',
      requestId: 'string',
      success: 'boolean',
    };
  }

  validate() {
    if(this.data && typeof (this.data as any).validate === 'function') {
      (this.data as any).validate();
    }
    super.validate();
  }

  constructor(map?: { [key: string]: any }) {
    super(map);
  }
}

