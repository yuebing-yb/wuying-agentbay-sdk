// This file is auto-generated, don't edit it
import * as $dara from '@darabonba/typescript';

export class DescribeNetworkRequest extends $dara.Model {
  authorization?: string;
  networkId?: string;
  static names(): { [key: string]: string } {
    return {
      authorization: 'Authorization',
      networkId: 'NetworkId',
    };
  }

  static types(): { [key: string]: any } {
    return {
      authorization: 'string',
      networkId: 'string',
    };
  }

  validate() {
    super.validate();
  }

  constructor(map?: { [key: string]: any }) {
    super(map);
  }
}


