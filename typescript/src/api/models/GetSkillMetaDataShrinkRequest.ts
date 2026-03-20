// This file is auto-generated, don't edit it
import * as $dara from '@darabonba/typescript';


export class GetSkillMetaDataShrinkRequest extends $dara.Model {
  authorization?: string;
  imageId?: string;
  skillGroupIdsShrink?: string;
  static names(): { [key: string]: string } {
    return {
      authorization: 'Authorization',
      imageId: 'ImageId',
      skillGroupIdsShrink: 'SkillGroupIds',
    };
  }

  static types(): { [key: string]: any } {
    return {
      authorization: 'string',
      imageId: 'string',
      skillGroupIdsShrink: 'string',
    };
  }

  validate() {
    super.validate();
  }

  constructor(map?: { [key: string]: any }) {
    super(map);
  }
}
