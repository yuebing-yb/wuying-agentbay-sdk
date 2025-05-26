// This file is auto-generated, don't edit it
import * as $dara from '@darabonba/typescript';


export class ListMcpToolsRequest extends $dara.Model {
  authorization?: string;
  static names(): { [key: string]: string } {
    return {
      authorization: 'Authorization',
    };
  }

  static types(): { [key: string]: any } {
    return {
      authorization: 'string',
    };
  }

  validate() {
    super.validate();
  }

  constructor(map?: { [key: string]: any }) {
    super(map);
  }
}

