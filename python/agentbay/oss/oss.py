import json
from typing import Any, Dict, Optional

from agentbay.api.base_service import BaseService
from ..logger import get_logger, log_api_response
from agentbay.exceptions import AgentBayError, OssError
from agentbay.model import ApiResponse

# Initialize logger for this module
logger = get_logger("oss")


class OSSClientResult(ApiResponse):
    """Result of OSS client creation operations."""

    def __init__(
        self,
        request_id: str = "",
        success: bool = False,
        client_config: Optional[Dict[str, Any]] = None,
        error_message: str = "",
    ):
        """
        Initialize an OSSClientResult.

        Args:
            request_id (str, optional): Unique identifier for the API request.
                Defaults to "".
            success (bool, optional): Whether the operation was successful.
                Defaults to False.
            client_config (Dict[str, Any], optional): OSS client configuration.
                Defaults to None.
            error_message (str, optional): Error message if the operation failed.
                Defaults to "".
        """
        super().__init__(request_id)
        self.success = success
        self.client_config = client_config or {}
        self.error_message = error_message


class OSSUploadResult(ApiResponse):
    """Result of OSS upload operations."""

    def __init__(
        self,
        request_id: str = "",
        success: bool = False,
        content: str = "",
        error_message: str = "",
    ):
        """
        Initialize an OSSUploadResult.

        Args:
            request_id (str, optional): Unique identifier for the API request.
                Defaults to "".
            success (bool, optional): Whether the operation was successful.
                Defaults to False.
            content (str, optional): Result of the upload operation. Defaults to "".
            error_message (str, optional): Error message if the operation failed.
                Defaults to "".
        """
        super().__init__(request_id)
        self.success = success
        self.content = content
        self.error_message = error_message


class OSSDownloadResult(ApiResponse):
    """Result of OSS download operations."""

    def __init__(
        self,
        request_id: str = "",
        success: bool = False,
        content: str = "",
        error_message: str = "",
    ):
        """
        Initialize an OSSDownloadResult.

        Args:
            request_id (str, optional): Unique identifier for the API request.
                Defaults to "".
            success (bool, optional): Whether the operation was successful.
                Defaults to False.
            content (string, optional): Defaults to "Download success"
            error_message (str, optional): Error message if the operation failed.
                Defaults to "".
        """
        super().__init__(request_id)
        self.success = success
        self.content = content
        self.error_message = error_message


class Oss(BaseService):
    """
    Handles Object Storage Service operations in the AgentBay cloud environment.
    """

    def __init__(self, session):
        """
        Initialize an Oss object.

        Args:
            session: The Session instance that this Oss belongs to.
        """
        super().__init__(session)

    def _handle_error(self, e):
        """
        Convert AgentBayError to OssError for compatibility.

        Args:
            e (Exception): The exception to convert.

        Returns:
            OssError: The converted exception.
        """
        if isinstance(e, OssError):
            return e
        if isinstance(e, AgentBayError):
            return OssError(str(e))
        return e

    def env_init(
        self,
        access_key_id: str,
        access_key_secret: str,
        securityToken: Optional[str] = None,
        endpoint: Optional[str] = None,
        region: Optional[str] = None,
    ) -> OSSClientResult:
        """
        Create an OSS client with the provided credentials.

        Args:
            access_key_id: The Access Key ID for OSS authentication.
            access_key_secret: The Access Key Secret for OSS authentication.
            securityToken: Optional security token for temporary credentials.
            endpoint: The OSS service endpoint. If not specified, the default is used.
            region: The OSS region. If not specified, the default is used.

        Returns:
            OSSClientResult: Result object containing client configuration and error
                message if any.

        Example:
            ```python
            from agentbay import AgentBay

            agent_bay = AgentBay(api_key="your_api_key")

            def initialize_oss_environment():
                try:
                    result = agent_bay.create()
                    if result.success:
                        session = result.session

                        # Initialize OSS environment
                        oss_result = session.oss.env_init(
                            access_key_id="your_access_key_id",
                            access_key_secret="your_access_key_secret",
                            securityToken="your_security_token",
                            endpoint="oss-cn-hangzhou.aliyuncs.com",
                            region="cn-hangzhou"
                        )

                        if oss_result.success:
                            print(f"OSS environment initialized successfully")
                            print(f"Request ID: {oss_result.request_id}")
                        else:
                            print(f"Failed to initialize OSS: {oss_result.error_message}")

                        session.delete()
                except Exception as e:
                    print(f"Error: {e}")

            initialize_oss_environment()
            ```
        """
        try:
            args = {
                "access_key_id": access_key_id,
                "access_key_secret": access_key_secret,
                "security_token": securityToken,
            }

            # Add optional parameters if provided
            if endpoint:
                args["endpoint"] = endpoint
            if region:
                args["region"] = region

            result = self.session.call_mcp_tool("oss_env_init", args)
            try:
                response_body = json.dumps(
                    getattr(result, "body", result), ensure_ascii=False, indent=2
                )
                log_api_response(response_body)
            except Exception:
                logger.debug(f"📥 Response: {result}")

            if result.success:
                try:
                    client_config = result.data
                    return OSSClientResult(
                        request_id=result.request_id,
                        success=True,
                        client_config=client_config,
                    )
                except json.JSONDecodeError:
                    return OSSClientResult(
                        request_id=result.request_id,
                        success=False,
                        error_message="Failed to parse client configuration JSON",
                    )
            else:
                return OSSClientResult(
                    request_id=result.request_id,
                    success=False,
                    error_message=result.error_message
                    or "Failed to initialize OSS environment",
                )
        except AgentBayError as e:
            return OSSClientResult(request_id="", success=False, error_message=str(e))
        except Exception as e:
            return OSSClientResult(
                request_id="",
                success=False,
                error_message=f"Failed to initialize OSS environment: {e}",
            )

    def upload(self, bucket: str, object: str, path: str) -> OSSUploadResult:
        """
        Upload a local file or directory to OSS.

        Note: Before calling this API, you must first call env_init to initialize
            the OSS environment.

        Args:
            bucket: OSS bucket name.
            object: Object key in OSS.
            path: Local file or directory path to upload.

        Returns:
            OSSUploadResult: Result object containing upload result and error message
                if any.

        Example:
            ```python
            from agentbay import AgentBay

            agent_bay = AgentBay(api_key="your_api_key")

            def upload_file_to_oss():
                try:
                    result = agent_bay.create()
                    if result.success:
                        session = result.session

                        # Step 1: Initialize OSS environment
                        session.oss.env_init(
                            access_key_id="your_access_key_id",
                            access_key_secret="your_access_key_secret",
                            endpoint="oss-cn-hangzhou.aliyuncs.com",
                            region="cn-hangzhou"
                        )

                        # Step 2: Upload file
                        upload_result = session.oss.upload(
                            bucket="my-bucket",
                            object="my-object",
                            path="/path/to/local/file"
                        )

                        if upload_result.success:
                            print(f"File uploaded successfully")
                            print(f"Content: {upload_result.content}")
                        else:
                            print(f"Upload failed: {upload_result.error_message}")

                        session.delete()
                except Exception as e:
                    print(f"Error: {e}")

            upload_file_to_oss()
            ```
        """
        try:
            args = {"bucket": bucket, "object": object, "path": path}

            result = self.session.call_mcp_tool("oss_upload", args)
            logger.debug(f"📥 OSS Response: {result}")

            if result.success:
                return OSSUploadResult(
                    request_id=result.request_id,
                    success=True,
                    content=result.data,
                )
            else:
                return OSSUploadResult(
                    request_id=result.request_id,
                    success=False,
                    error_message=result.error_message or "Failed to upload to OSS",
                )
        except AgentBayError as e:
            return OSSUploadResult(request_id="", success=False, error_message=str(e))
        except Exception as e:
            return OSSUploadResult(
                request_id="",
                success=False,
                error_message=f"Failed to upload to OSS: {e}",
            )

    def upload_anonymous(self, url: str, path: str) -> OSSUploadResult:
        """
        Upload a local file or directory to a URL anonymously.

        Args:
            url: The HTTP/HTTPS URL to upload the file to.
            path: Local file or directory path to upload.

        Returns:
            OSSUploadResult: Result object containing upload result and error message
                if any.

        Example:
            ```python
            from agentbay import AgentBay

            agent_bay = AgentBay(api_key="your_api_key")

            def upload_file_anonymously():
                try:
                    result = agent_bay.create()
                    if result.success:
                        session = result.session

                        # Upload file anonymously to a URL
                        upload_result = session.oss.upload_anonymous(
                            url="https://example.com/upload",
                            path="/path/to/local/file"
                        )

                        if upload_result.success:
                            print(f"File uploaded anonymously successfully")
                            print(f"Content: {upload_result.content}")
                        else:
                            print(f"Upload failed: {upload_result.error_message}")

                        session.delete()
                except Exception as e:
                    print(f"Error: {e}")

            upload_file_anonymously()
            ```
        """
        try:
            args = {"url": url, "path": path}

            result = self.session.call_mcp_tool("oss_upload_annon", args)
            logger.debug(f"📥 OSS Response: {result}")

            if result.success:
                return OSSUploadResult(
                    request_id=result.request_id,
                    success=True,
                    content=result.data,
                )
            else:
                return OSSUploadResult(
                    request_id=result.request_id,
                    success=False,
                    error_message=result.error_message
                    or "Failed to upload anonymously",
                )
        except AgentBayError as e:
            return OSSUploadResult(request_id="", success=False, error_message=str(e))
        except Exception as e:
            return OSSUploadResult(
                request_id="",
                success=False,
                error_message=f"Failed to upload anonymously: {e}",
            )

    def download(self, bucket: str, object: str, path: str) -> OSSDownloadResult:
        """
        Download an object from OSS to a local file or directory.

        Note: Before calling this API, you must first call env_init to initialize
            the OSS environment.

        Args:
            bucket: OSS bucket name.
            object: Object key in OSS.
            path: Local file or directory path to download to.

        Returns:
            OSSDownloadResult: Result object containing download status and error
                message if any.

        Example:
            ```python
            from agentbay import AgentBay

            agent_bay = AgentBay(api_key="your_api_key")

            def download_file_from_oss():
                try:
                    result = agent_bay.create()
                    if result.success:
                        session = result.session

                        # Step 1: Initialize OSS environment
                        session.oss.env_init(
                            access_key_id="your_access_key_id",
                            access_key_secret="your_access_key_secret",
                            endpoint="oss-cn-hangzhou.aliyuncs.com",
                            region="cn-hangzhou"
                        )

                        # Step 2: Download file
                        download_result = session.oss.download(
                            bucket="my-bucket",
                            object="my-object",
                            path="/path/to/local/file"
                        )

                        if download_result.success:
                            print(f"File downloaded successfully")
                            print(f"Content: {download_result.content}")
                        else:
                            print(f"Download failed: {download_result.error_message}")

                        session.delete()
                except Exception as e:
                    print(f"Error: {e}")

            download_file_from_oss()
            ```
        """
        try:
            args = {"bucket": bucket, "object": object, "path": path}

            result = self.session.call_mcp_tool("oss_download", args)
            logger.debug(f"📥 OSS Response: {result}")

            if result.success:
                return OSSDownloadResult(
                    request_id=result.request_id,
                    success=True,
                    content=result.data,
                )
            else:
                return OSSDownloadResult(
                    request_id=result.request_id,
                    success=False,
                    error_message=result.error_message or "Failed to download from OSS",
                )
        except AgentBayError as e:
            return OSSDownloadResult(request_id="", success=False, error_message=str(e))
        except Exception as e:
            return OSSDownloadResult(
                request_id="",
                success=False,
                error_message=f"Failed to download from OSS: {e}",
            )

    def download_anonymous(self, url: str, path: str) -> OSSDownloadResult:
        """
        Download a file from a URL anonymously to a local file path.

        Args:
            url: The HTTP/HTTPS URL to download the file from.
            path: Local file or directory path to download to.

        Returns:
            OSSDownloadResult: Result object containing download status and error
                message if any.

        Example:
            ```python
            from agentbay import AgentBay

            agent_bay = AgentBay(api_key="your_api_key")

            def download_file_anonymously():
                try:
                    result = agent_bay.create()
                    if result.success:
                        session = result.session

                        # Download file anonymously from a URL
                        download_result = session.oss.download_anonymous(
                            url="https://example.com/file.txt",
                            path="/path/to/local/file.txt"
                        )

                        if download_result.success:
                            print(f"File downloaded anonymously successfully")
                            print(f"Content: {download_result.content}")
                        else:
                            print(f"Download failed: {download_result.error_message}")

                        session.delete()
                except Exception as e:
                    print(f"Error: {e}")

            download_file_anonymously()
            ```
        """
        try:
            args = {"url": url, "path": path}

            result = self.session.call_mcp_tool("oss_download_annon", args)
            logger.debug(f"📥 OSS Response: {result}")

            if result.success:
                return OSSDownloadResult(
                    request_id=result.request_id,
                    success=True,
                    content=result.data,
                )
            else:
                return OSSDownloadResult(
                    request_id=result.request_id,
                    success=False,
                    error_message=result.error_message
                    or "Failed to download anonymously",
                )
        except AgentBayError as e:
            return OSSDownloadResult(request_id="", success=False, error_message=str(e))
        except Exception as e:
            return OSSDownloadResult(
                request_id="",
                success=False,
                error_message=f"Failed to download anonymously: {e}",
            )
