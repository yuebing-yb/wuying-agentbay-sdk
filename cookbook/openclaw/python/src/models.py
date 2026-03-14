"""
Pydantic models for OpenClaw session management API.
Fields match Java version's CreateSessionRequest and SessionResponse.
"""

from typing import Optional

from pydantic import BaseModel, Field


class CreateSessionRequest(BaseModel):
    """Request model for creating a new OpenClaw session."""

    agentbay_api_key: str = Field(..., alias="agentbayApiKey", description="AgentBay API Key (required)")
    bailian_api_key: str = Field(..., alias="bailianApiKey", description="Bailian API Key (required)")
    username: str = Field(..., description="Username (required)")
    dingtalk_client_id: Optional[str] = Field(None, alias="dingtalkClientId", description="DingTalk Client ID (optional)")
    dingtalk_client_secret: Optional[str] = Field(None, alias="dingtalkClientSecret", description="DingTalk Client Secret (optional)")
    feishu_app_id: Optional[str] = Field(None, alias="feishuAppId", description="Feishu App ID (optional)")
    feishu_app_secret: Optional[str] = Field(None, alias="feishuAppSecret", description="Feishu App Secret (optional)")
    model_base_url: Optional[str] = Field(None, alias="modelBaseUrl", description="Model Base URL (optional)")
    model_id: Optional[str] = Field(None, alias="modelId", description="Model ID (optional)")

    model_config = {
        "populate_by_name": True,
    }


class SessionResponse(BaseModel):
    """Response model for session information."""

    session_id: str = Field(..., alias="sessionId", description="Session ID")
    resource_url: str = Field(..., alias="resourceUrl", description="Desktop resource URL")
    openclaw_url: str = Field(..., alias="openclawUrl", description="OpenClaw UI URL")
    username: str = Field(..., description="Username")
    created_at: str = Field(..., alias="createdAt", description="Creation timestamp")
    status: str = Field(..., description="Session status")

    model_config = {
        "populate_by_name": True,
        "by_alias": True,
    }


class DingtalkSetupStatus(BaseModel):
    """Status of one-click DingTalk setup flow."""

    step: str = Field(..., description="login | creating | done | error")
    client_id: Optional[str] = Field(None, alias="clientId")
    client_secret: Optional[str] = Field(None, alias="clientSecret")
    error: Optional[str] = Field(None, description="Error message if step=error")
    backend: Optional[str] = Field(None, description="operator | agent")
    applied: Optional[bool] = Field(None, description="Whether credentials were auto-applied to config")
    apply_error: Optional[str] = Field(None, alias="applyError", description="Error if auto-apply failed")

    model_config = {"populate_by_name": True, "by_alias": True}


class FeishuSetupStatus(BaseModel):
    """Status of one-click Feishu setup flow."""

    step: str = Field(..., description="login | creating | done | error")
    app_id: Optional[str] = Field(None, alias="appId")
    app_secret: Optional[str] = Field(None, alias="appSecret")
    error: Optional[str] = Field(None, description="Error message if step=error")
    backend: Optional[str] = Field(None, description="playwright")
    applied: Optional[bool] = Field(None, description="Whether credentials were auto-applied to config")
    apply_error: Optional[str] = Field(None, alias="applyError", description="Error if auto-apply failed")

    model_config = {"populate_by_name": True, "by_alias": True}


class SessionInfo(BaseModel):
    """Internal session information storage."""

    session_id: str
    resource_url: str
    openclaw_url: str
    username: str
    created_at: str
    status: str
    agent_bay: object = Field(exclude=True)  # Exclude from serialization
    session: object = Field(exclude=True)  # Exclude from serialization
    create_request: Optional[CreateSessionRequest] = Field(
        default=None, exclude=True
    )  # For config rebuild

    model_config = {
        "arbitrary_types_allowed": True,
    }

    def to_response(self) -> SessionResponse:
        """Convert to API response model."""
        return SessionResponse(
            session_id=self.session_id,
            resource_url=self.resource_url,
            openclaw_url=self.openclaw_url,
            username=self.username,
            created_at=self.created_at,
            status=self.status,
        )
