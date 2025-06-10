import json
from typing import Optional

from agentbay.api.models import CallMcpToolRequest
from agentbay.exceptions import OssError


class Oss:
    """
    Handles Object Storage Service operations in the AgentBay cloud environment.
    """

    def __init__(self, session):
        """
        Initialize an Oss object.

        Args:
            session: The Session instance that this Oss belongs to.
        """
        self.session = session

    def create_client(self, access_key_id: str, access_key_secret: str, 
                     endpoint: Optional[str] = None, region: Optional[str] = None) -> str:
        """
        Create an OSS client with the provided credentials.

        Args:
            access_key_id: The Access Key ID for OSS authentication.
            access_key_secret: The Access Key Secret for OSS authentication.
            endpoint: The OSS service endpoint. If not specified, the default is used.
            region: The OSS region. If not specified, the default is used.

        Returns:
            str: The result of the client creation operation.

        Raises:
            OssError: If the client creation fails.
        """
        try:
            args = {
                "access_key_id": access_key_id,
                "access_key_secret": access_key_secret
            }
            
            # Add optional parameters if provided
            if endpoint:
                args["endpoint"] = endpoint
            if region:
                args["region"] = region
                
            args_json = json.dumps(args, ensure_ascii=False)

            request = CallMcpToolRequest(
                authorization=f"Bearer {self.session.get_api_key()}",
                session_id=self.session.get_session_id(),
                name="oss_client_create",
                args=args_json,
            )
            print("request =", request)
            response = self.session.get_client().call_mcp_tool(request)
            print("response =", response)
            
            data = response.to_map().get("body", {}).get("Data", {})
            result = data.get("result")
            
            if not isinstance(result, str):
                raise OssError("result field not found or not a string")
                
            return result
        except Exception as e:
            raise OssError(f"Failed to create OSS client: {e}")

    def upload(self, bucket: str, object: str, path: str) -> str:
        """
        Upload a local file or directory to OSS.

        Args:
            bucket: OSS bucket name.
            object: Object key in OSS.
            path: Local file or directory path to upload.

        Returns:
            str: The result of the upload operation.

        Raises:
            OssError: If the upload fails.
        """
        try:
            args = {
                "bucket": bucket,
                "object": object,
                "path": path
            }
            args_json = json.dumps(args, ensure_ascii=False)

            request = CallMcpToolRequest(
                authorization=f"Bearer {self.session.get_api_key()}",
                session_id=self.session.get_session_id(),
                name="oss_upload",
                args=args_json,
            )
            print("request =", request)
            response = self.session.get_client().call_mcp_tool(request)
            print("response =", response)
            
            data = response.to_map().get("body", {}).get("Data", {})
            result = data.get("result")
            
            if not isinstance(result, str):
                raise OssError("result field not found or not a string")
                
            return result
        except Exception as e:
            raise OssError(f"Failed to upload to OSS: {e}")

    def upload_anonymous(self, url: str, path: str) -> str:
        """
        Upload a local file or directory to a URL anonymously.

        Args:
            url: The HTTP/HTTPS URL to upload the file to.
            path: Local file or directory path to upload.

        Returns:
            str: The result of the upload operation.

        Raises:
            OssError: If the upload fails.
        """
        try:
            args = {
                "url": url,
                "path": path
            }
            args_json = json.dumps(args, ensure_ascii=False)

            request = CallMcpToolRequest(
                authorization=f"Bearer {self.session.get_api_key()}",
                session_id=self.session.get_session_id(),
                name="oss_upload_annon",
                args=args_json,
            )
            print("request =", request)
            response = self.session.get_client().call_mcp_tool(request)
            print("response =", response)
            
            data = response.to_map().get("body", {}).get("Data", {})
            result = data.get("result")
            
            if not isinstance(result, str):
                raise OssError("result field not found or not a string")
                
            return result
        except Exception as e:
            raise OssError(f"Failed to upload anonymously: {e}")

    def download(self, bucket: str, object: str, path: str) -> str:
        """
        Download an object from OSS to a local file.

        Args:
            bucket: OSS bucket name.
            object: Object key in OSS.
            path: Local path to save the downloaded file.

        Returns:
            str: The result of the download operation.

        Raises:
            OssError: If the download fails.
        """
        try:
            args = {
                "bucket": bucket,
                "object": object,
                "path": path
            }
            args_json = json.dumps(args, ensure_ascii=False)

            request = CallMcpToolRequest(
                authorization=f"Bearer {self.session.get_api_key()}",
                session_id=self.session.get_session_id(),
                name="oss_download",
                args=args_json,
            )
            print("request =", request)
            response = self.session.get_client().call_mcp_tool(request)
            print("response =", response)
            
            data = response.to_map().get("body", {}).get("Data", {})
            result = data.get("result")
            
            if not isinstance(result, str):
                raise OssError("result field not found or not a string")
                
            return result
        except Exception as e:
            raise OssError(f"Failed to download from OSS: {e}")

    def download_anonymous(self, url: str, path: str) -> str:
        """
        Download a file from a URL anonymously to a local file.

        Args:
            url: The HTTP/HTTPS URL to download the file from.
            path: The full local file path to save the downloaded file.

        Returns:
            str: The result of the download operation.

        Raises:
            OssError: If the download fails.
        """
        try:
            args = {
                "url": url,
                "path": path
            }
            args_json = json.dumps(args, ensure_ascii=False)

            request = CallMcpToolRequest(
                authorization=f"Bearer {self.session.get_api_key()}",
                session_id=self.session.get_session_id(),
                name="oss_download_annon",
                args=args_json,
            )
            print("request =", request)
            response = self.session.get_client().call_mcp_tool(request)
            print("response =", response)
            
            data = response.to_map().get("body", {}).get("Data", {})
            result = data.get("result")
            
            if not isinstance(result, str):
                raise OssError("result field not found or not a string")
                
            return result
        except Exception as e:
            raise OssError(f"Failed to download anonymously: {e}")
