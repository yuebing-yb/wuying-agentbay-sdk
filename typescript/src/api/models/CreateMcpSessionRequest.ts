// This file is auto-generated, don't edit it
import * as $dara from '@darabonba/typescript';


export class CreateMcpSessionRequest extends $dara.Model {
  authorization?: string;
  externalUserId?: string;
  sessionId?: string;
  static names(): { [key: string]: string } {
    return {
      authorization: 'Authorization',
      externalUserId: 'ExternalUserId',
      sessionId: 'SessionId',
    };
  }

  static types(): { [key: string]: any } {
    return {
      authorization: 'string',
      externalUserId: 'string',
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

