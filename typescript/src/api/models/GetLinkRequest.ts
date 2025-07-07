// This file is auto-generated, don't edit it
import * as $dara from "@darabonba/typescript";

export class GetLinkRequest extends $dara.Model {
  authorization?: string;
  sessionId?: string;
  protocolType?: string;
  port?: number;
  static names(): { [key: string]: string } {
    return {
      authorization: "Authorization",
      sessionId: "SessionId",
      protocolType: "ProtocolType",
      port: "Port",
    };
  }

  static types(): { [key: string]: any } {
    return {
      authorization: "string",
      sessionId: "string",
      protocolType: "string",
      port: "number",
    };
  }

  validate() {
    super.validate();
  }

  constructor(map?: { [key: string]: any }) {
    super(map);
  }
}
