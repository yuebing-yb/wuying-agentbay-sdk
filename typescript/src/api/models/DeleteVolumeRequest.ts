// This file is auto-generated, don't edit it
import * as $dara from '@darabonba/typescript';


export class DeleteVolumeRequest extends $dara.Model {
  authorization?: string;
  /**
   * @remarks
   * This parameter is required.
   */
  volumeId?: string;
  static names(): { [key: string]: string } {
    return {
      authorization: 'Authorization',
      volumeId: 'VolumeId',
    };
  }

  static types(): { [key: string]: any } {
    return {
      authorization: 'string',
      volumeId: 'string',
    };
  }

  validate() {
    super.validate();
  }

  constructor(map?: { [key: string]: any }) {
    super(map);
  }
}

