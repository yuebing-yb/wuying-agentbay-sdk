// This file is auto-generated, don't edit it
import * as $dara from "@darabonba/typescript";
import OpenApi from "@alicloud/openapi-core";
import { OpenApiUtil, $OpenApiUtil } from "@alicloud/openapi-core";

import * as $_model from "./models/model";
export * from "./models/model";

export class Client extends OpenApi {
  constructor(config: $OpenApiUtil.Config) {
    super(config);
    this._signatureAlgorithm = "v2";
    this._endpointRule = "";
    this.checkConfig(config);
    this._endpoint = this.getEndpoint(
      "wuyingai",
      this._regionId,
      this._endpointRule,
      this._network,
      this._suffix,
      this._endpointMap,
      this._endpoint
    );
  }

  getEndpoint(
    productId: string,
    regionId: string,
    endpointRule: string,
    network: string,
    suffix: string,
    endpointMap: { [key: string]: string },
    endpoint: string
  ): string {
    if (!$dara.isNull(endpoint)) {
      return endpoint;
    }

    if (!$dara.isNull(endpointMap) && !$dara.isNull(endpointMap[regionId])) {
      return endpointMap[regionId];
    }

    return OpenApiUtil.getEndpointRules(
      productId,
      regionId,
      endpointRule,
      network,
      suffix
    );
  }

  /**
   * 调用mcp工具
   *
   * @param request - CallMcpToolRequest
   * @param runtime - runtime options for this request RuntimeOptions
   * @returns CallMcpToolResponse
   */
  async callMcpToolWithOptions(
    request: $_model.CallMcpToolRequest,
    runtime: $dara.RuntimeOptions
  ): Promise<$_model.CallMcpToolResponse> {
    request.validate();
    const body: { [key: string]: any } = {};
    if (!$dara.isNull(request.args)) {
      body["Args"] = request.args;
    }

    if (!$dara.isNull(request.authorization)) {
      body["Authorization"] = request.authorization;
    }

    if (!$dara.isNull(request.externalUserId)) {
      body["ExternalUserId"] = request.externalUserId;
    }

    if (!$dara.isNull(request.imageId)) {
      body["ImageId"] = request.imageId;
    }

    if (!$dara.isNull(request.name)) {
      body["Name"] = request.name;
    }

    if (!$dara.isNull(request.server)) {
      body["Server"] = request.server;
    }

    if (!$dara.isNull(request.sessionId)) {
      body["SessionId"] = request.sessionId;
    }

    if (!$dara.isNull(request.tool)) {
      body["Tool"] = request.tool;
    }

    const req = new $OpenApiUtil.OpenApiRequest({
      body: OpenApiUtil.parseToMap(body),
    });
    const params = new $OpenApiUtil.Params({
      action: "CallMcpTool",
      version: "2025-05-06",
      protocol: "HTTPS",
      pathname: "/",
      method: "POST",
      authType: "Anonymous",
      style: "RPC",
      reqBodyType: "formData",
      bodyType: "json",
    });
    return $dara.cast<$_model.CallMcpToolResponse>(
      await this.callApi(params, req, runtime),
      new $_model.CallMcpToolResponse({})
    );
  }

  /**
   * 调用mcp工具
   *
   * @param request - CallMcpToolRequest
   * @returns CallMcpToolResponse
   */
  async callMcpTool(
    request: $_model.CallMcpToolRequest
  ): Promise<$_model.CallMcpToolResponse> {
    const runtime = new $dara.RuntimeOptions({});
    return await this.callMcpToolWithOptions(request, runtime);
  }

  /**
   * 创建 mcp session
   *
   * @param tmpReq - CreateMcpSessionRequest
   * @param runtime - runtime options for this request RuntimeOptions
   * @returns CreateMcpSessionResponse
   */
  async createMcpSessionWithOptions(
    tmpReq: $_model.CreateMcpSessionRequest,
    runtime: $dara.RuntimeOptions
  ): Promise<$_model.CreateMcpSessionResponse> {
    tmpReq.validate();
    const request = new $_model.CreateMcpSessionShrinkRequest({});
    OpenApiUtil.convert(tmpReq, request);
    if (!$dara.isNull(tmpReq.persistenceDataList)) {
      request.persistenceDataListShrink =
        OpenApiUtil.arrayToStringWithSpecifiedStyle(
          tmpReq.persistenceDataList,
          "PersistenceDataList",
          "json"
        );
    }

    const body: { [key: string]: any } = {};
    if (!$dara.isNull(request.authorization)) {
      body["Authorization"] = request.authorization;
    }

    if (!$dara.isNull(request.contextId)) {
      body["ContextId"] = request.contextId;
    }

    if (!$dara.isNull(request.externalUserId)) {
      body["ExternalUserId"] = request.externalUserId;
    }

    if (!$dara.isNull(request.imageId)) {
      body["ImageId"] = request.imageId;
    }

    if (!$dara.isNull(request.labels)) {
      body["Labels"] = request.labels;
    }

    if (!$dara.isNull(request.persistenceDataListShrink)) {
      body["PersistenceDataList"] = request.persistenceDataListShrink;
    }

    if (!$dara.isNull(request.sessionId)) {
      body["SessionId"] = request.sessionId;
    }

    const req = new $OpenApiUtil.OpenApiRequest({
      body: OpenApiUtil.parseToMap(body),
    });
    const params = new $OpenApiUtil.Params({
      action: "CreateMcpSession",
      version: "2025-05-06",
      protocol: "HTTPS",
      pathname: "/",
      method: "POST",
      authType: "Anonymous",
      style: "RPC",
      reqBodyType: "formData",
      bodyType: "json",
    });
    return $dara.cast<$_model.CreateMcpSessionResponse>(
      await this.callApi(params, req, runtime),
      new $_model.CreateMcpSessionResponse({})
    );
  }

  /**
   * 创建 mcp session
   *
   * @param request - CreateMcpSessionRequest
   * @returns CreateMcpSessionResponse
   */
  async createMcpSession(
    request: $_model.CreateMcpSessionRequest
  ): Promise<$_model.CreateMcpSessionResponse> {
    const runtime = new $dara.RuntimeOptions({});
    return await this.createMcpSessionWithOptions(request, runtime);
  }

  /**
   * 删除持久化上下文
   *
   * @param request - DeleteContextRequest
   * @param runtime - runtime options for this request RuntimeOptions
   * @returns DeleteContextResponse
   */
  async deleteContextWithOptions(
    request: $_model.DeleteContextRequest,
    runtime: $dara.RuntimeOptions
  ): Promise<$_model.DeleteContextResponse> {
    request.validate();
    const body: { [key: string]: any } = {};
    if (!$dara.isNull(request.authorization)) {
      body["Authorization"] = request.authorization;
    }

    if (!$dara.isNull(request.id)) {
      body["Id"] = request.id;
    }

    const req = new $OpenApiUtil.OpenApiRequest({
      body: OpenApiUtil.parseToMap(body),
    });
    const params = new $OpenApiUtil.Params({
      action: "DeleteContext",
      version: "2025-05-06",
      protocol: "HTTPS",
      pathname: "/",
      method: "POST",
      authType: "Anonymous",
      style: "RPC",
      reqBodyType: "formData",
      bodyType: "json",
    });
    return $dara.cast<$_model.DeleteContextResponse>(
      await this.callApi(params, req, runtime),
      new $_model.DeleteContextResponse({})
    );
  }

  /**
   * 删除持久化上下文
   *
   * @param request - DeleteContextRequest
   * @returns DeleteContextResponse
   */
  async deleteContext(
    request: $_model.DeleteContextRequest
  ): Promise<$_model.DeleteContextResponse> {
    const runtime = new $dara.RuntimeOptions({});
    return await this.deleteContextWithOptions(request, runtime);
  }

  /**
   * 获取上下文
   *
   * @param request - GetContextRequest
   * @param runtime - runtime options for this request RuntimeOptions
   * @returns GetContextResponse
   */
  async getContextWithOptions(
    request: $_model.GetContextRequest,
    runtime: $dara.RuntimeOptions
  ): Promise<$_model.GetContextResponse> {
    request.validate();
    const body: { [key: string]: any } = {};
    if (!$dara.isNull(request.allowCreate)) {
      body["AllowCreate"] = request.allowCreate;
    }

    if (!$dara.isNull(request.authorization)) {
      body["Authorization"] = request.authorization;
    }

    if (!$dara.isNull(request.name)) {
      body["Name"] = request.name;
    }

    const req = new $OpenApiUtil.OpenApiRequest({
      body: OpenApiUtil.parseToMap(body),
    });
    const params = new $OpenApiUtil.Params({
      action: "GetContext",
      version: "2025-05-06",
      protocol: "HTTPS",
      pathname: "/",
      method: "POST",
      authType: "Anonymous",
      style: "RPC",
      reqBodyType: "formData",
      bodyType: "json",
    });
    return $dara.cast<$_model.GetContextResponse>(
      await this.callApi(params, req, runtime),
      new $_model.GetContextResponse({})
    );
  }

  /**
   * 获取上下文
   *
   * @param request - GetContextRequest
   * @returns GetContextResponse
   */
  async getContext(
    request: $_model.GetContextRequest
  ): Promise<$_model.GetContextResponse> {
    const runtime = new $dara.RuntimeOptions({});
    return await this.getContextWithOptions(request, runtime);
  }

  /**
   * 获取上下文信息
   *
   * @param request - GetContextInfoRequest
   * @param runtime - runtime options for this request RuntimeOptions
   * @returns GetContextInfoResponse
   */
  async getContextInfoWithOptions(
    request: $_model.GetContextInfoRequest,
    runtime: $dara.RuntimeOptions
  ): Promise<$_model.GetContextInfoResponse> {
    request.validate();
    const body: { [key: string]: any } = {};
    if (!$dara.isNull(request.authorization)) {
      body["Authorization"] = request.authorization;
    }

    if (!$dara.isNull(request.contextId)) {
      body["ContextId"] = request.contextId;
    }

    if (!$dara.isNull(request.path)) {
      body["Path"] = request.path;
    }

    if (!$dara.isNull(request.sessionId)) {
      body["SessionId"] = request.sessionId;
    }

    if (!$dara.isNull(request.taskType)) {
      body["TaskType"] = request.taskType;
    }

    const req = new $OpenApiUtil.OpenApiRequest({
      body: OpenApiUtil.parseToMap(body),
    });
    const params = new $OpenApiUtil.Params({
      action: "GetContextInfo",
      version: "2025-05-06",
      protocol: "HTTPS",
      pathname: "/",
      method: "POST",
      authType: "Anonymous",
      style: "RPC",
      reqBodyType: "formData",
      bodyType: "json",
    });
    return $dara.cast<$_model.GetContextInfoResponse>(
      await this.callApi(params, req, runtime),
      new $_model.GetContextInfoResponse({})
    );
  }

  /**
   * 获取上下文信息
   *
   * @param request - GetContextInfoRequest
   * @returns GetContextInfoResponse
   */
  async getContextInfo(
    request: $_model.GetContextInfoRequest
  ): Promise<$_model.GetContextInfoResponse> {
    const runtime = new $dara.RuntimeOptions({});
    return await this.getContextInfoWithOptions(request, runtime);
  }

  /**
   * 获取标签
   *
   * @param request - GetLabelRequest
   * @param runtime - runtime options for this request RuntimeOptions
   * @returns GetLabelResponse
   */
  async getLabelWithOptions(
    request: $_model.GetLabelRequest,
    runtime: $dara.RuntimeOptions
  ): Promise<$_model.GetLabelResponse> {
    request.validate();
    const body: { [key: string]: any } = {};
    if (!$dara.isNull(request.authorization)) {
      body["Authorization"] = request.authorization;
    }

    if (!$dara.isNull(request.maxResults)) {
      body["MaxResults"] = request.maxResults;
    }

    if (!$dara.isNull(request.nextToken)) {
      body["NextToken"] = request.nextToken;
    }

    if (!$dara.isNull(request.sessionId)) {
      body["SessionId"] = request.sessionId;
    }

    const req = new $OpenApiUtil.OpenApiRequest({
      body: OpenApiUtil.parseToMap(body),
    });
    const params = new $OpenApiUtil.Params({
      action: "GetLabel",
      version: "2025-05-06",
      protocol: "HTTPS",
      pathname: "/",
      method: "POST",
      authType: "Anonymous",
      style: "RPC",
      reqBodyType: "formData",
      bodyType: "json",
    });
    return $dara.cast<$_model.GetLabelResponse>(
      await this.callApi(params, req, runtime),
      new $_model.GetLabelResponse({})
    );
  }

  /**
   * 获取标签
   *
   * @param request - GetLabelRequest
   * @returns GetLabelResponse
   */
  async getLabel(
    request: $_model.GetLabelRequest
  ): Promise<$_model.GetLabelResponse> {
    const runtime = new $dara.RuntimeOptions({});
    return await this.getLabelWithOptions(request, runtime);
  }

  /**
   * 获取特定端口的转发链接
   *
   * @param request - GetLinkRequest
   * @param runtime - runtime options for this request RuntimeOptions
   * @returns GetLinkResponse
   */
  async getLinkWithOptions(
    request: $_model.GetLinkRequest,
    runtime: $dara.RuntimeOptions
  ): Promise<$_model.GetLinkResponse> {
    request.validate();
    const body: { [key: string]: any } = {};
    if (!$dara.isNull(request.authorization)) {
      body["Authorization"] = request.authorization;
    }

    if (!$dara.isNull(request.port)) {
      body["Port"] = request.port;
    }

    if (!$dara.isNull(request.protocolType)) {
      body["ProtocolType"] = request.protocolType;
    }

    if (!$dara.isNull(request.sessionId)) {
      body["SessionId"] = request.sessionId;
    }

    const req = new $OpenApiUtil.OpenApiRequest({
      body: OpenApiUtil.parseToMap(body),
    });
    const params = new $OpenApiUtil.Params({
      action: "GetLink",
      version: "2025-05-06",
      protocol: "HTTPS",
      pathname: "/",
      method: "POST",
      authType: "Anonymous",
      style: "RPC",
      reqBodyType: "formData",
      bodyType: "json",
    });
    return $dara.cast<$_model.GetLinkResponse>(
      await this.callApi(params, req, runtime),
      new $_model.GetLinkResponse({})
    );
  }

  /**
   * 获取特定端口的转发链接
   *
   * @param request - GetLinkRequest
   * @returns GetLinkResponse
   */
  async getLink(
    request: $_model.GetLinkRequest
  ): Promise<$_model.GetLinkResponse> {
    const runtime = new $dara.RuntimeOptions({});
    return await this.getLinkWithOptions(request, runtime);
  }

  /**
   * 获取mcp资源信息
   *
   * @param request - GetMcpResourceRequest
   * @param runtime - runtime options for this request RuntimeOptions
   * @returns GetMcpResourceResponse
   */
  async getMcpResourceWithOptions(
    request: $_model.GetMcpResourceRequest,
    runtime: $dara.RuntimeOptions
  ): Promise<$_model.GetMcpResourceResponse> {
    request.validate();
    const body: { [key: string]: any } = {};
    if (!$dara.isNull(request.authorization)) {
      body["Authorization"] = request.authorization;
    }

    if (!$dara.isNull(request.sessionId)) {
      body["SessionId"] = request.sessionId;
    }

    const req = new $OpenApiUtil.OpenApiRequest({
      body: OpenApiUtil.parseToMap(body),
    });
    const params = new $OpenApiUtil.Params({
      action: "GetMcpResource",
      version: "2025-05-06",
      protocol: "HTTPS",
      pathname: "/",
      method: "POST",
      authType: "Anonymous",
      style: "RPC",
      reqBodyType: "formData",
      bodyType: "json",
    });
    return $dara.cast<$_model.GetMcpResourceResponse>(
      await this.callApi(params, req, runtime),
      new $_model.GetMcpResourceResponse({})
    );
  }

  /**
   * 获取mcp资源信息
   *
   * @param request - GetMcpResourceRequest
   * @returns GetMcpResourceResponse
   */
  async getMcpResource(
    request: $_model.GetMcpResourceRequest
  ): Promise<$_model.GetMcpResourceResponse> {
    const runtime = new $dara.RuntimeOptions({});
    return await this.getMcpResourceWithOptions(request, runtime);
  }

  /**
   * 获取上下文列表
   *
   * @param request - ListContextsRequest
   * @param runtime - runtime options for this request RuntimeOptions
   * @returns ListContextsResponse
   */
  async listContextsWithOptions(
    request: $_model.ListContextsRequest,
    runtime: $dara.RuntimeOptions
  ): Promise<$_model.ListContextsResponse> {
    request.validate();
    const body: { [key: string]: any } = {};
    if (!$dara.isNull(request.authorization)) {
      body["Authorization"] = request.authorization;
    }

    if (!$dara.isNull(request.maxResults)) {
      body["MaxResults"] = request.maxResults;
    }

    if (!$dara.isNull(request.nextToken)) {
      body["NextToken"] = request.nextToken;
    }

    const req = new $OpenApiUtil.OpenApiRequest({
      body: OpenApiUtil.parseToMap(body),
    });
    const params = new $OpenApiUtil.Params({
      action: "ListContexts",
      version: "2025-05-06",
      protocol: "HTTPS",
      pathname: "/",
      method: "POST",
      authType: "Anonymous",
      style: "RPC",
      reqBodyType: "formData",
      bodyType: "json",
    });
    return $dara.cast<$_model.ListContextsResponse>(
      await this.callApi(params, req, runtime),
      new $_model.ListContextsResponse({})
    );
  }

  /**
   * 获取上下文列表
   *
   * @param request - ListContextsRequest
   * @returns ListContextsResponse
   */
  async listContexts(
    request: $_model.ListContextsRequest
  ): Promise<$_model.ListContextsResponse> {
    const runtime = new $dara.RuntimeOptions({});
    return await this.listContextsWithOptions(request, runtime);
  }

  /**
   * ListMcpTools
   *
   * @param request - ListMcpToolsRequest
   * @param runtime - runtime options for this request RuntimeOptions
   * @returns ListMcpToolsResponse
   */
  async listMcpToolsWithOptions(
    request: $_model.ListMcpToolsRequest,
    runtime: $dara.RuntimeOptions
  ): Promise<$_model.ListMcpToolsResponse> {
    request.validate();
    const body: { [key: string]: any } = {};
    if (!$dara.isNull(request.authorization)) {
      body["Authorization"] = request.authorization;
    }

    if (!$dara.isNull(request.imageId)) {
      body["ImageId"] = request.imageId;
    }

    const req = new $OpenApiUtil.OpenApiRequest({
      body: OpenApiUtil.parseToMap(body),
    });
    const params = new $OpenApiUtil.Params({
      action: "ListMcpTools",
      version: "2025-05-06",
      protocol: "HTTPS",
      pathname: "/",
      method: "POST",
      authType: "Anonymous",
      style: "RPC",
      reqBodyType: "formData",
      bodyType: "json",
    });
    return $dara.cast<$_model.ListMcpToolsResponse>(
      await this.callApi(params, req, runtime),
      new $_model.ListMcpToolsResponse({})
    );
  }

  /**
   * ListMcpTools
   *
   * @param request - ListMcpToolsRequest
   * @returns ListMcpToolsResponse
   */
  async listMcpTools(
    request: $_model.ListMcpToolsRequest
  ): Promise<$_model.ListMcpToolsResponse> {
    const runtime = new $dara.RuntimeOptions({});
    return await this.listMcpToolsWithOptions(request, runtime);
  }

  /**
   * 根据Lable查询Session列表
   *
   * @param request - ListSessionRequest
   * @param runtime - runtime options for this request RuntimeOptions
   * @returns ListSessionResponse
   */
  async listSessionWithOptions(
    request: $_model.ListSessionRequest,
    runtime: $dara.RuntimeOptions
  ): Promise<$_model.ListSessionResponse> {
    request.validate();
    const body: { [key: string]: any } = {};
    if (!$dara.isNull(request.authorization)) {
      body["Authorization"] = request.authorization;
    }

    if (!$dara.isNull(request.labels)) {
      body["Labels"] = request.labels;
    }

    if (!$dara.isNull(request.maxResults)) {
      body["MaxResults"] = request.maxResults;
    }

    if (!$dara.isNull(request.nextToken)) {
      body["NextToken"] = request.nextToken;
    }

    const req = new $OpenApiUtil.OpenApiRequest({
      body: OpenApiUtil.parseToMap(body),
    });
    const params = new $OpenApiUtil.Params({
      action: "ListSession",
      version: "2025-05-06",
      protocol: "HTTPS",
      pathname: "/",
      method: "POST",
      authType: "Anonymous",
      style: "RPC",
      reqBodyType: "formData",
      bodyType: "json",
    });
    return $dara.cast<$_model.ListSessionResponse>(
      await this.callApi(params, req, runtime),
      new $_model.ListSessionResponse({})
    );
  }

  /**
   * 根据Lable查询Session列表
   *
   * @param request - ListSessionRequest
   * @returns ListSessionResponse
   */
  async listSession(
    request: $_model.ListSessionRequest
  ): Promise<$_model.ListSessionResponse> {
    const runtime = new $dara.RuntimeOptions({});
    return await this.listSessionWithOptions(request, runtime);
  }

  /**
   * 修改上下文
   *
   * @param request - ModifyContextRequest
   * @param runtime - runtime options for this request RuntimeOptions
   * @returns ModifyContextResponse
   */
  async modifyContextWithOptions(
    request: $_model.ModifyContextRequest,
    runtime: $dara.RuntimeOptions
  ): Promise<$_model.ModifyContextResponse> {
    request.validate();
    const body: { [key: string]: any } = {};
    if (!$dara.isNull(request.authorization)) {
      body["Authorization"] = request.authorization;
    }

    if (!$dara.isNull(request.id)) {
      body["Id"] = request.id;
    }

    if (!$dara.isNull(request.name)) {
      body["Name"] = request.name;
    }

    const req = new $OpenApiUtil.OpenApiRequest({
      body: OpenApiUtil.parseToMap(body),
    });
    const params = new $OpenApiUtil.Params({
      action: "ModifyContext",
      version: "2025-05-06",
      protocol: "HTTPS",
      pathname: "/",
      method: "POST",
      authType: "Anonymous",
      style: "RPC",
      reqBodyType: "formData",
      bodyType: "json",
    });
    return $dara.cast<$_model.ModifyContextResponse>(
      await this.callApi(params, req, runtime),
      new $_model.ModifyContextResponse({})
    );
  }

  /**
   * 修改上下文
   *
   * @param request - ModifyContextRequest
   * @returns ModifyContextResponse
   */
  async modifyContext(
    request: $_model.ModifyContextRequest
  ): Promise<$_model.ModifyContextResponse> {
    const runtime = new $dara.RuntimeOptions({});
    return await this.modifyContextWithOptions(request, runtime);
  }

  /**
   * 释放 mcp session
   *
   * @param request - ReleaseMcpSessionRequest
   * @param runtime - runtime options for this request RuntimeOptions
   * @returns ReleaseMcpSessionResponse
   */
  async releaseMcpSessionWithOptions(
    request: $_model.ReleaseMcpSessionRequest,
    runtime: $dara.RuntimeOptions
  ): Promise<$_model.ReleaseMcpSessionResponse> {
    request.validate();
    const body: { [key: string]: any } = {};
    if (!$dara.isNull(request.authorization)) {
      body["Authorization"] = request.authorization;
    }

    if (!$dara.isNull(request.sessionId)) {
      body["SessionId"] = request.sessionId;
    }

    const req = new $OpenApiUtil.OpenApiRequest({
      body: OpenApiUtil.parseToMap(body),
    });
    const params = new $OpenApiUtil.Params({
      action: "ReleaseMcpSession",
      version: "2025-05-06",
      protocol: "HTTPS",
      pathname: "/",
      method: "POST",
      authType: "Anonymous",
      style: "RPC",
      reqBodyType: "formData",
      bodyType: "json",
    });
    return $dara.cast<$_model.ReleaseMcpSessionResponse>(
      await this.callApi(params, req, runtime),
      new $_model.ReleaseMcpSessionResponse({})
    );
  }

  /**
   * 释放 mcp session
   *
   * @param request - ReleaseMcpSessionRequest
   * @returns ReleaseMcpSessionResponse
   */
  async releaseMcpSession(
    request: $_model.ReleaseMcpSessionRequest
  ): Promise<$_model.ReleaseMcpSessionResponse> {
    const runtime = new $dara.RuntimeOptions({});
    return await this.releaseMcpSessionWithOptions(request, runtime);
  }

  /**
   * 设置标签
   *
   * @param request - SetLabelRequest
   * @param runtime - runtime options for this request RuntimeOptions
   * @returns SetLabelResponse
   */
  async setLabelWithOptions(
    request: $_model.SetLabelRequest,
    runtime: $dara.RuntimeOptions
  ): Promise<$_model.SetLabelResponse> {
    request.validate();
    const body: { [key: string]: any } = {};
    if (!$dara.isNull(request.authorization)) {
      body["Authorization"] = request.authorization;
    }

    if (!$dara.isNull(request.labels)) {
      body["Labels"] = request.labels;
    }

    if (!$dara.isNull(request.sessionId)) {
      body["SessionId"] = request.sessionId;
    }

    const req = new $OpenApiUtil.OpenApiRequest({
      body: OpenApiUtil.parseToMap(body),
    });
    const params = new $OpenApiUtil.Params({
      action: "SetLabel",
      version: "2025-05-06",
      protocol: "HTTPS",
      pathname: "/",
      method: "POST",
      authType: "Anonymous",
      style: "RPC",
      reqBodyType: "formData",
      bodyType: "json",
    });
    return $dara.cast<$_model.SetLabelResponse>(
      await this.callApi(params, req, runtime),
      new $_model.SetLabelResponse({})
    );
  }

  /**
   * 设置标签
   *
   * @param request - SetLabelRequest
   * @returns SetLabelResponse
   */
  async setLabel(
    request: $_model.SetLabelRequest
  ): Promise<$_model.SetLabelResponse> {
    const runtime = new $dara.RuntimeOptions({});
    return await this.setLabelWithOptions(request, runtime);
  }

  /**
   * 同步上下文
   *
   * @param request - SyncContextRequest
   * @param runtime - runtime options for this request RuntimeOptions
   * @returns SyncContextResponse
   */
  async syncContextWithOptions(
    request: $_model.SyncContextRequest,
    runtime: $dara.RuntimeOptions
  ): Promise<$_model.SyncContextResponse> {
    request.validate();
    const query: { [key: string]: any } = {};
    if (!$dara.isNull(request.authorization)) {
      query["Authorization"] = request.authorization;
    }

    const body: { [key: string]: any } = {};
    if (!$dara.isNull(request.contextId)) {
      body["ContextId"] = request.contextId;
    }

    if (!$dara.isNull(request.mode)) {
      body["Mode"] = request.mode;
    }

    if (!$dara.isNull(request.path)) {
      body["Path"] = request.path;
    }

    if (!$dara.isNull(request.sessionId)) {
      body["SessionId"] = request.sessionId;
    }

    const req = new $OpenApiUtil.OpenApiRequest({
      query: OpenApiUtil.query(query),
      body: OpenApiUtil.parseToMap(body),
    });
    const params = new $OpenApiUtil.Params({
      action: "SyncContext",
      version: "2025-05-06",
      protocol: "HTTPS",
      pathname: "/",
      method: "POST",
      authType: "Anonymous",
      style: "RPC",
      reqBodyType: "formData",
      bodyType: "json",
    });
    return $dara.cast<$_model.SyncContextResponse>(
      await this.callApi(params, req, runtime),
      new $_model.SyncContextResponse({})
    );
  }

  /**
   * 同步上下文
   *
   * @param request - SyncContextRequest
   * @returns SyncContextResponse
   */
  async syncContext(
    request: $_model.SyncContextRequest
  ): Promise<$_model.SyncContextResponse> {
    const runtime = new $dara.RuntimeOptions({});
    return await this.syncContextWithOptions(request, runtime);
  }
}
