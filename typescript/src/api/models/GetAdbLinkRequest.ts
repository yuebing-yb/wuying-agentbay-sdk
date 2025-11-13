// This file is auto-generated, don't edit it
import * as $dara from '@darabonba/typescript';

export class GetAdbLinkRequest extends $dara.Model {
  authorization?: string;
  option?: string;
  sessionId?: string;
  
  static names(): { [key: string]: string } {
    return {
      authorization: 'Authorization',
      option: 'Option',
      sessionId: 'SessionId',
    };
  }

  static types(): { [key: string]: any } {
    return {
      authorization: 'string',
      option: 'string',
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

