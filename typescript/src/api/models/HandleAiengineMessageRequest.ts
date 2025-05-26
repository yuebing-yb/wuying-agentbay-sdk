// This file is auto-generated, don't edit it
import * as $dara from '@darabonba/typescript';


export class HandleAIEngineMessageRequest extends $dara.Model {
  msgType?: string;
  sessionToken?: string;
  body?: string;
  static names(): { [key: string]: string } {
    return {
      msgType: 'MsgType',
      sessionToken: 'SessionToken',
      body: 'body',
    };
  }

  static types(): { [key: string]: any } {
    return {
      msgType: 'string',
      sessionToken: 'string',
      body: 'string',
    };
  }

  validate() {
    super.validate();
  }

  constructor(map?: { [key: string]: any }) {
    super(map);
  }
}

