// This file is auto-generated, don't edit it
import * as $dara from '@darabonba/typescript';


export class GetSkillMetaDataRequest extends $dara.Model {
  authorization?: string;
  imageId?: string;
  skillGroupIds?: string[];
  static names(): { [key: string]: string } {
    return {
      authorization: 'Authorization',
      imageId: 'ImageId',
      skillGroupIds: 'SkillGroupIds',
    };
  }

  static types(): { [key: string]: any } {
    return {
      authorization: 'string',
      imageId: 'string',
      skillGroupIds: { 'type': 'array', 'itemType': 'string' },
    };
  }

  validate() {
    if(Array.isArray(this.skillGroupIds)) {
      $dara.Model.validateArray(this.skillGroupIds);
    }
    super.validate();
  }

  constructor(map?: { [key: string]: any }) {
    super(map);
  }
}
