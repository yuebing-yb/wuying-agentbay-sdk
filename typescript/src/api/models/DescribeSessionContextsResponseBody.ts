// This file is auto-generated, don't edit it
import * as $dara from '@darabonba/typescript';


export class DescribeSessionContextsResponseBodyData extends $dara.Model {
  bindTime?: string;
  contextId?: string;
  contextName?: string;
  path?: string;
  policy?: string;
  static names(): { [key: string]: string } {
    return {
      bindTime: 'BindTime',
      contextId: 'ContextId',
      contextName: 'ContextName',
      path: 'Path',
      policy: 'Policy',
    };
  }

  static types(): { [key: string]: any } {
    return {
      bindTime: 'string',
      contextId: 'string',
      contextName: 'string',
      path: 'string',
      policy: 'string',
    };
  }

  validate() {
    super.validate();
  }

  constructor(map?: { [key: string]: any }) {
    super(map);
  }
}

export class DescribeSessionContextsResponseBody extends $dara.Model {
  code?: string;
  data?: DescribeSessionContextsResponseBodyData[];
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
      data: { 'type': 'array', 'itemType': DescribeSessionContextsResponseBodyData },
      httpStatusCode: 'number',
      message: 'string',
      requestId: 'string',
      success: 'boolean',
    };
  }

  validate() {
    if(Array.isArray(this.data)) {
      $dara.Model.validateArray(this.data);
    }
    super.validate();
  }

  constructor(map?: { [key: string]: any }) {
    super(map);
  }
}

