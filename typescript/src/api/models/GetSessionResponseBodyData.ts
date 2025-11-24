// This file is auto-generated, don't edit it
import * as $dara from '@darabonba/typescript';


export class GetSessionResponseBodyDataContexts extends $dara.Model {
  id?: string;
  name?: string;
  static names(): { [key: string]: string } {
    return {
      id: 'id',
      name: 'name',
    };
  }

  static types(): { [key: string]: any } {
    return {
      id: 'string',
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

export class GetSessionResponseBodyData extends $dara.Model {
  appInstanceId?: string;
  resourceId?: string;
  sessionId?: string;
  success?: boolean;
  httpPort?: string;
  networkInterfaceIp?: string;
  token?: string;
  vpcResource?: boolean;
  resourceUrl?: string;
  status?: string;
  contexts?: GetSessionResponseBodyDataContexts[];
  static names(): { [key: string]: string } {
    return {
      appInstanceId: 'AppInstanceId',
      resourceId: 'ResourceId',
      sessionId: 'SessionId',
      success: 'Success',
      httpPort: 'HttpPort',
      networkInterfaceIp: 'NetworkInterfaceIp',
      token: 'Token',
      vpcResource: 'VpcResource',
      resourceUrl: 'ResourceUrl',
      status: 'Status',
      contexts: 'contexts',
    };
  }

  static types(): { [key: string]: any } {
    return {
      appInstanceId: 'string',
      resourceId: 'string',
      sessionId: 'string',
      success: 'boolean',
      httpPort: 'string',
      networkInterfaceIp: 'string',
      token: 'string',
      vpcResource: 'boolean',
      contexts: { 'type': 'array', 'itemType': GetSessionResponseBodyDataContexts },
      resourceUrl: 'string',
      status: 'string',
    };
  }

  validate() {
    if(Array.isArray(this.contexts)) {
      $dara.Model.validateArray(this.contexts);
    }
    super.validate();
  }

  constructor(map?: { [key: string]: any }) {
    super(map);
  }
}

