// This file is auto-generated, don't edit it
import * as $dara from '@darabonba/typescript';


export class GetContextRequest extends $dara.Model {
  allowCreate?: boolean;
  authorization?: string;
  contextId?: string;
  name?: string;
  loginRegionId?: string;
  static names(): { [key: string]: string } {
    return {
      allowCreate: 'AllowCreate',
      authorization: 'Authorization',
      contextId: 'ContextId',
      name: 'Name',
      loginRegionId: 'LoginRegionId',
    };
  }

  static types(): { [key: string]: any } {
    return {
      allowCreate: 'boolean',
      authorization: 'string',
      contextId: 'string',
      name: 'string',
      loginRegionId: 'string',
    };
  }

  validate() {
    super.validate();
  }

  constructor(map?: { [key: string]: any }) {
    super(map);
  }
}

