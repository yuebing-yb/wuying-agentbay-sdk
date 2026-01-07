// This file is auto-generated, don't edit it
import * as $dara from '@darabonba/typescript';


export class ListVolumesRequest extends $dara.Model {
  authorization?: string;
  imageId?: string;
  maxResults?: number;
  nextToken?: string;
  volumeIds?: string[];
  volumeName?: string;
  static names(): { [key: string]: string } {
    return {
      authorization: 'Authorization',
      imageId: 'ImageId',
      maxResults: 'MaxResults',
      nextToken: 'NextToken',
      volumeIds: 'VolumeIds',
      volumeName: 'VolumeName',
    };
  }

  static types(): { [key: string]: any } {
    return {
      authorization: 'string',
      imageId: 'string',
      maxResults: 'number',
      nextToken: 'string',
      volumeIds: { 'type': 'array', 'itemType': 'string' },
      volumeName: 'string',
    };
  }

  validate() {
    if(Array.isArray(this.volumeIds)) {
      $dara.Model.validateArray(this.volumeIds);
    }
    super.validate();
  }

  constructor(map?: { [key: string]: any }) {
    super(map);
  }
}

