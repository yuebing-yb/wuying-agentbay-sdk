// This file is auto-generated, don't edit it
import * as $dara from '@darabonba/typescript';


export class BindContextsShrinkRequest extends $dara.Model {
  authorization?: string;
  persistenceDataListShrink?: string;
  sessionId?: string;
  static names(): { [key: string]: string } {
    return {
      authorization: 'Authorization',
      persistenceDataListShrink: 'PersistenceDataList',
      sessionId: 'SessionId',
    };
  }

  static types(): { [key: string]: any } {
    return {
      authorization: 'string',
      persistenceDataListShrink: 'string',
      sessionId: 'string',
    };
  }

  validate() {
    super.validate();
  }

  constructor(map?: { [key: string]: any }) {
    super(map);
  }
}

