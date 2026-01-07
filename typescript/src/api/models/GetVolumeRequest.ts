// This file is auto-generated, don't edit it
import * as $dara from '@darabonba/typescript';


export class GetVolumeRequest extends $dara.Model {
  allowCreate?: boolean;
  authorization?: string;
  imageId?: string;
  volumeName?: string;
  static names(): { [key: string]: string } {
    return {
      allowCreate: 'AllowCreate',
      authorization: 'Authorization',
      imageId: 'ImageId',
      volumeName: 'VolumeName',
    };
  }

  static types(): { [key: string]: any } {
    return {
      allowCreate: 'boolean',
      authorization: 'string',
      imageId: 'string',
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

