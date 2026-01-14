// This file is auto-generated, don't edit it
import * as $dara from '@darabonba/typescript';


export class CreateMcpSessionResponseBodyData extends $dara.Model {
  appInstanceId?: string;
  errMsg?: string;
  httpPort?: string;
  linkUrl?: string;
  networkInterfaceIp?: string;
  resourceId?: string;
  resourceUrl?: string;
  sessionId?: string;
  success?: boolean;
  token?: string;
  toolList?: string;
  vpcResource?: boolean;
  static names(): { [key: string]: string } {
    return {
      appInstanceId: 'AppInstanceId',
      errMsg: 'ErrMsg',
      httpPort: 'HttpPort',
      linkUrl: 'LinkUrl',
      networkInterfaceIp: 'NetworkInterfaceIp',
      resourceId: 'ResourceId',
      resourceUrl: 'ResourceUrl',
      sessionId: 'SessionId',
      success: 'Success',
      token: 'Token',
      toolList: 'ToolList',
      vpcResource: 'VpcResource',
    };
  }

  static types(): { [key: string]: any } {
    return {
      appInstanceId: 'string',
      errMsg: 'string',
      httpPort: 'string',
      linkUrl: 'string',
      networkInterfaceIp: 'string',
      resourceId: 'string',
      resourceUrl: 'string',
      sessionId: 'string',
      success: 'boolean',
      token: 'string',
      toolList: 'string',
      vpcResource: 'boolean',
    };
  }

  validate() {
    super.validate();
  }

  constructor(map?: { [key: string]: any }) {
    super(map);
  }
}

