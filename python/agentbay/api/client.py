# -*- coding: utf-8 -*-
# This file is auto-generated, don't edit it. Thanks.
from __future__ import annotations
from alibabacloud_tea_openapi.client import Client as OpenApiClient
from alibabacloud_tea_openapi import utils_models as open_api_util_models
from darabonba.core import DaraCore as DaraCore
from alibabacloud_tea_openapi.utils import Utils
from agentbay.api import models as main_models
from darabonba.runtime import RuntimeOptions
from typing import Dict


"""
"""


class Client(OpenApiClient):

    def __init__(
        self,
        config: open_api_util_models.Config,
    ):
        super().__init__(config)
        self._signature_algorithm = "v2"
        self._endpoint_rule = ""
        self.check_config(config)
        self._endpoint = self.get_endpoint(
            "wuyingai",
            self._region_id,
            self._endpoint_rule,
            self._network,
            self._suffix,
            self._endpoint_map,
            self._endpoint,
        )

    def get_endpoint(
        self,
        product_id: str,
        region_id: str,
        endpoint_rule: str,
        network: str,
        suffix: str,
        endpoint_map: Dict[str, str],
        endpoint: str,
    ) -> str:
        if not DaraCore.is_null(endpoint):
            return endpoint
        if not DaraCore.is_null(endpoint_map) and not DaraCore.is_null(
            endpoint_map.get(region_id)
        ):
            return endpoint_map.get(region_id)
        return Utils.get_endpoint_rules(
            product_id, region_id, endpoint_rule, network, suffix
        )

    def call_mcp_tool_with_options(
        self,
        request: main_models.CallMcpToolRequest,
        runtime: RuntimeOptions,
    ) -> main_models.CallMcpToolResponse:
        request.validate()
        body = {}
        if not DaraCore.is_null(request.args):
            body["Args"] = request.args
        if not DaraCore.is_null(request.authorization):
            body["Authorization"] = request.authorization
        if not DaraCore.is_null(request.external_user_id):
            body["ExternalUserId"] = request.external_user_id
        if not DaraCore.is_null(request.name):
            body["Name"] = request.name
        if not DaraCore.is_null(request.server):
            body["Server"] = request.server
        if not DaraCore.is_null(request.session_id):
            body["SessionId"] = request.session_id
        if not DaraCore.is_null(request.tool):
            body["Tool"] = request.tool
        req = open_api_util_models.OpenApiRequest(body=Utils.parse_to_map(body))
        params = open_api_util_models.Params(
            action="CallMcpTool",
            version="2025-05-06",
            protocol="HTTPS",
            pathname="/",
            method="POST",
            auth_type="Anonymous",
            style="RPC",
            req_body_type="formData",
            body_type="json",
        )
        return DaraCore.from_map(
            main_models.CallMcpToolResponse(), self.call_api(params, req, runtime)
        )

    async def call_mcp_tool_with_options_async(
        self,
        request: main_models.CallMcpToolRequest,
        runtime: RuntimeOptions,
    ) -> main_models.CallMcpToolResponse:
        request.validate()
        body = {}
        if not DaraCore.is_null(request.args):
            body["Args"] = request.args
        if not DaraCore.is_null(request.authorization):
            body["Authorization"] = request.authorization
        if not DaraCore.is_null(request.external_user_id):
            body["ExternalUserId"] = request.external_user_id
        if not DaraCore.is_null(request.name):
            body["Name"] = request.name
        if not DaraCore.is_null(request.server):
            body["Server"] = request.server
        if not DaraCore.is_null(request.session_id):
            body["SessionId"] = request.session_id
        if not DaraCore.is_null(request.tool):
            body["Tool"] = request.tool
        req = open_api_util_models.OpenApiRequest(body=Utils.parse_to_map(body))
        params = open_api_util_models.Params(
            action="CallMcpTool",
            version="2025-05-06",
            protocol="HTTPS",
            pathname="/",
            method="POST",
            auth_type="Anonymous",
            style="RPC",
            req_body_type="formData",
            body_type="json",
        )
        return DaraCore.from_map(
            main_models.CallMcpToolResponse(),
            await self.call_api_async(params, req, runtime),
        )

    def call_mcp_tool(
        self,
        request: main_models.CallMcpToolRequest,
    ) -> main_models.CallMcpToolResponse:
        runtime = RuntimeOptions()
        return self.call_mcp_tool_with_options(request, runtime)

    async def call_mcp_tool_async(
        self,
        request: main_models.CallMcpToolRequest,
    ) -> main_models.CallMcpToolResponse:
        runtime = RuntimeOptions()
        return await self.call_mcp_tool_with_options_async(request, runtime)

    def create_mcp_session_with_options(
        self,
        request: main_models.CreateMcpSessionRequest,
        runtime: RuntimeOptions,
    ) -> main_models.CreateMcpSessionResponse:
        request.validate()
        body = {}
        if not DaraCore.is_null(request.authorization):
            body["Authorization"] = request.authorization
        if not DaraCore.is_null(request.external_user_id):
            body["ExternalUserId"] = request.external_user_id
        if not DaraCore.is_null(request.session_id):
            body["SessionId"] = request.session_id
        req = open_api_util_models.OpenApiRequest(body=Utils.parse_to_map(body))
        params = open_api_util_models.Params(
            action="CreateMcpSession",
            version="2025-05-06",
            protocol="HTTPS",
            pathname="/",
            method="POST",
            auth_type="Anonymous",
            style="RPC",
            req_body_type="formData",
            body_type="json",
        )
        return DaraCore.from_map(
            main_models.CreateMcpSessionResponse(), self.call_api(params, req, runtime)
        )

    async def create_mcp_session_with_options_async(
        self,
        request: main_models.CreateMcpSessionRequest,
        runtime: RuntimeOptions,
    ) -> main_models.CreateMcpSessionResponse:
        request.validate()
        body = {}
        if not DaraCore.is_null(request.authorization):
            body["Authorization"] = request.authorization
        if not DaraCore.is_null(request.external_user_id):
            body["ExternalUserId"] = request.external_user_id
        if not DaraCore.is_null(request.session_id):
            body["SessionId"] = request.session_id
        req = open_api_util_models.OpenApiRequest(body=Utils.parse_to_map(body))
        params = open_api_util_models.Params(
            action="CreateMcpSession",
            version="2025-05-06",
            protocol="HTTPS",
            pathname="/",
            method="POST",
            auth_type="Anonymous",
            style="RPC",
            req_body_type="formData",
            body_type="json",
        )
        return DaraCore.from_map(
            main_models.CreateMcpSessionResponse(),
            await self.call_api_async(params, req, runtime),
        )

    def create_mcp_session(
        self,
        request: main_models.CreateMcpSessionRequest,
    ) -> main_models.CreateMcpSessionResponse:
        runtime = RuntimeOptions()
        return self.create_mcp_session_with_options(request, runtime)

    async def create_mcp_session_async(
        self,
        request: main_models.CreateMcpSessionRequest,
    ) -> main_models.CreateMcpSessionResponse:
        runtime = RuntimeOptions()
        return await self.create_mcp_session_with_options_async(request, runtime)

    def get_mcp_resource_with_options(
        self,
        request: main_models.GetMcpResourceRequest,
        runtime: RuntimeOptions,
    ) -> main_models.GetMcpResourceResponse:
        request.validate()
        body = {}
        if not DaraCore.is_null(request.authorization):
            body["Authorization"] = request.authorization
        if not DaraCore.is_null(request.session_id):
            body["SessionId"] = request.session_id
        req = open_api_util_models.OpenApiRequest(body=Utils.parse_to_map(body))
        params = open_api_util_models.Params(
            action="GetMcpResource",
            version="2025-05-06",
            protocol="HTTPS",
            pathname="/",
            method="POST",
            auth_type="Anonymous",
            style="RPC",
            req_body_type="formData",
            body_type="json",
        )
        return DaraCore.from_map(
            main_models.GetMcpResourceResponse(), self.call_api(params, req, runtime)
        )

    async def get_mcp_resource_with_options_async(
        self,
        request: main_models.GetMcpResourceRequest,
        runtime: RuntimeOptions,
    ) -> main_models.GetMcpResourceResponse:
        request.validate()
        body = {}
        if not DaraCore.is_null(request.authorization):
            body["Authorization"] = request.authorization
        if not DaraCore.is_null(request.session_id):
            body["SessionId"] = request.session_id
        req = open_api_util_models.OpenApiRequest(body=Utils.parse_to_map(body))
        params = open_api_util_models.Params(
            action="GetMcpResource",
            version="2025-05-06",
            protocol="HTTPS",
            pathname="/",
            method="POST",
            auth_type="Anonymous",
            style="RPC",
            req_body_type="formData",
            body_type="json",
        )
        return DaraCore.from_map(
            main_models.GetMcpResourceResponse(),
            await self.call_api_async(params, req, runtime),
        )

    def get_mcp_resource(
        self,
        request: main_models.GetMcpResourceRequest,
    ) -> main_models.GetMcpResourceResponse:
        runtime = RuntimeOptions()
        return self.get_mcp_resource_with_options(request, runtime)

    async def get_mcp_resource_async(
        self,
        request: main_models.GetMcpResourceRequest,
    ) -> main_models.GetMcpResourceResponse:
        runtime = RuntimeOptions()
        return await self.get_mcp_resource_with_options_async(request, runtime)

    def list_mcp_tools_with_options(
        self,
        request: main_models.ListMcpToolsRequest,
        runtime: RuntimeOptions,
    ) -> main_models.ListMcpToolsResponse:
        request.validate()
        body = {}
        if not DaraCore.is_null(request.authorization):
            body["Authorization"] = request.authorization
        req = open_api_util_models.OpenApiRequest(body=Utils.parse_to_map(body))
        params = open_api_util_models.Params(
            action="ListMcpTools",
            version="2025-05-06",
            protocol="HTTPS",
            pathname="/",
            method="POST",
            auth_type="Anonymous",
            style="RPC",
            req_body_type="formData",
            body_type="json",
        )
        return DaraCore.from_map(
            main_models.ListMcpToolsResponse(), self.call_api(params, req, runtime)
        )

    async def list_mcp_tools_with_options_async(
        self,
        request: main_models.ListMcpToolsRequest,
        runtime: RuntimeOptions,
    ) -> main_models.ListMcpToolsResponse:
        request.validate()
        body = {}
        if not DaraCore.is_null(request.authorization):
            body["Authorization"] = request.authorization
        req = open_api_util_models.OpenApiRequest(body=Utils.parse_to_map(body))
        params = open_api_util_models.Params(
            action="ListMcpTools",
            version="2025-05-06",
            protocol="HTTPS",
            pathname="/",
            method="POST",
            auth_type="Anonymous",
            style="RPC",
            req_body_type="formData",
            body_type="json",
        )
        return DaraCore.from_map(
            main_models.ListMcpToolsResponse(),
            await self.call_api_async(params, req, runtime),
        )

    def list_mcp_tools(
        self,
        request: main_models.ListMcpToolsRequest,
    ) -> main_models.ListMcpToolsResponse:
        runtime = RuntimeOptions()
        return self.list_mcp_tools_with_options(request, runtime)

    async def list_mcp_tools_async(
        self,
        request: main_models.ListMcpToolsRequest,
    ) -> main_models.ListMcpToolsResponse:
        runtime = RuntimeOptions()
        return await self.list_mcp_tools_with_options_async(request, runtime)

    def release_mcp_session_with_options(
        self,
        request: main_models.ReleaseMcpSessionRequest,
        runtime: RuntimeOptions,
    ) -> main_models.ReleaseMcpSessionResponse:
        request.validate()
        body = {}
        if not DaraCore.is_null(request.authorization):
            body["Authorization"] = request.authorization
        if not DaraCore.is_null(request.session_id):
            body["SessionId"] = request.session_id
        req = open_api_util_models.OpenApiRequest(body=Utils.parse_to_map(body))
        params = open_api_util_models.Params(
            action="ReleaseMcpSession",
            version="2025-05-06",
            protocol="HTTPS",
            pathname="/",
            method="POST",
            auth_type="Anonymous",
            style="RPC",
            req_body_type="formData",
            body_type="json",
        )
        return DaraCore.from_map(
            main_models.ReleaseMcpSessionResponse(), self.call_api(params, req, runtime)
        )

    async def release_mcp_session_with_options_async(
        self,
        request: main_models.ReleaseMcpSessionRequest,
        runtime: RuntimeOptions,
    ) -> main_models.ReleaseMcpSessionResponse:
        request.validate()
        body = {}
        if not DaraCore.is_null(request.authorization):
            body["Authorization"] = request.authorization
        if not DaraCore.is_null(request.session_id):
            body["SessionId"] = request.session_id
        req = open_api_util_models.OpenApiRequest(body=Utils.parse_to_map(body))
        params = open_api_util_models.Params(
            action="ReleaseMcpSession",
            version="2025-05-06",
            protocol="HTTPS",
            pathname="/",
            method="POST",
            auth_type="Anonymous",
            style="RPC",
            req_body_type="formData",
            body_type="json",
        )
        return DaraCore.from_map(
            main_models.ReleaseMcpSessionResponse(),
            await self.call_api_async(params, req, runtime),
        )

    def release_mcp_session(
        self,
        request: main_models.ReleaseMcpSessionRequest,
    ) -> main_models.ReleaseMcpSessionResponse:
        runtime = RuntimeOptions()
        return self.release_mcp_session_with_options(request, runtime)

    async def release_mcp_session_async(
        self,
        request: main_models.ReleaseMcpSessionRequest,
    ) -> main_models.ReleaseMcpSessionResponse:
        runtime = RuntimeOptions()
        return await self.release_mcp_session_with_options_async(request, runtime)
