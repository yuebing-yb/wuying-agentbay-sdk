// This file is auto-generated, don't edit it
import * as $dara from '@darabonba/typescript';


export class GetSkillMetaDataResponseBodyDataMetaDataList extends $dara.Model {
  description?: string;
  name?: string;
  static names(): { [key: string]: string } {
    return {
      description: 'Description',
      name: 'Name',
    };
  }

  static types(): { [key: string]: any } {
    return {
      description: 'string',
      name: 'string',
    };
  }

  validate() {
    super.validate();
  }

  constructor(map?: { [key: string]: any }) {
    super(map);
  }
}

export class GetSkillMetaDataResponseBodyData extends $dara.Model {
  metaDataList?: GetSkillMetaDataResponseBodyDataMetaDataList[];
  skillPath?: string;
  static names(): { [key: string]: string } {
    return {
      metaDataList: 'MetaDataList',
      skillPath: 'SkillPath',
    };
  }

  static types(): { [key: string]: any } {
    return {
      metaDataList: { 'type': 'array', 'itemType': GetSkillMetaDataResponseBodyDataMetaDataList },
      skillPath: 'string',
    };
  }

  validate() {
    if(Array.isArray(this.metaDataList)) {
      $dara.Model.validateArray(this.metaDataList);
    }
    super.validate();
  }

  constructor(map?: { [key: string]: any }) {
    super(map);
  }
}

export class GetSkillMetaDataResponseBody extends $dara.Model {
  code?: string;
  data?: GetSkillMetaDataResponseBodyData;
  httpStatusCode?: number;
  message?: string;
  requestId?: string;
  success?: boolean;
  totalCount?: number;
  static names(): { [key: string]: string } {
    return {
      code: 'Code',
      data: 'Data',
      httpStatusCode: 'HttpStatusCode',
      message: 'Message',
      requestId: 'RequestId',
      success: 'Success',
      totalCount: 'TotalCount',
    };
  }

  static types(): { [key: string]: any } {
    return {
      code: 'string',
      data: GetSkillMetaDataResponseBodyData,
      httpStatusCode: 'number',
      message: 'string',
      requestId: 'string',
      success: 'boolean',
      totalCount: 'number',
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
