// This file is auto-generated, don't edit it
import * as $dara from '@darabonba/typescript';

export class CreateNetworkRequest extends $dara.Model {
  authorization?: string;
  loginRegionId?: string;
  networkId?: string;
  static names(): { [key: string]: string } {
    return {
      authorization: 'Authorization',
      loginRegionId: 'LoginRegionId',
      networkId: 'NetworkId',
    };
  }

  static types(): { [key: string]: any } {
    return {
      authorization: 'string',
      loginRegionId: 'string',
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


