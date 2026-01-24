// This file is auto-generated, don't edit it
import * as $dara from '@darabonba/typescript';

export class CreateNetworkResponseBodyData extends $dara.Model {
  networkId?: string;
  networkToken?: string;
  static names(): { [key: string]: string } {
    return {
      networkId: 'NetworkId',
      networkToken: 'NetworkToken',
    };
  }

  static types(): { [key: string]: any } {
    return {
      networkId: 'string',
      networkToken: 'string',
    };
  }

  validate() {
    super.validate();
  }

  constructor(map?: { [key: string]: any }) {
    super(map);
  }
}

export class CreateNetworkResponseBody extends $dara.Model {
  code?: string;
  data?: CreateNetworkResponseBodyData;
  httpStatusCode?: number;
  message?: string;
  requestId?: string;
  success?: boolean;
  static names(): { [key: string]: string } {
    return {
      code: 'Code',
      data: 'Data',
      httpStatusCode: 'HttpStatusCode',
      message: 'Message',
      requestId: 'RequestId',
      success: 'Success',
    };
  }

  static types(): { [key: string]: any } {
    return {
      code: 'string',
      data: CreateNetworkResponseBodyData,
      httpStatusCode: 'number',
      message: 'string',
      requestId: 'string',
      success: 'boolean',
    };
  }

  validate() {
    if (this.data && typeof (this.data as any).validate === 'function') {
      (this.data as any).validate();
    }
    super.validate();
  }

  constructor(map?: { [key: string]: any }) {
    super(map);
  }
}


