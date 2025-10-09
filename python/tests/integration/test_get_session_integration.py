"""Integration test for GetSession API"""
import os
import pytest
from agentbay import AgentBay


def test_get_session_api():
    """
    Integration test for GetSession API.
    Tests that the API correctly retrieves session information.
    """
    # Get API Key from environment
    api_key = os.getenv("AGENTBAY_API_KEY")
    if not api_key:
        pytest.fail("AGENTBAY_API_KEY environment variable is not set")

    # Initialize AgentBay client
    agent_bay = AgentBay(api_key=api_key)

    # Create a session first
    print("Creating a new session for GetSession testing...")
    create_result = agent_bay.create()
    assert create_result.success, f"Failed to create session: {create_result.error_message}"
    session = create_result.session
    session_id = session.session_id
    print(f"Session created with ID: {session_id}")

    try:
        # Test GetSession API
        print("Testing GetSession API...")
        get_session_result = agent_bay.get_session(session_id)

        # Validate response
        assert get_session_result.request_id, "RequestID should not be empty"
        print(f"GetSession RequestID: {get_session_result.request_id}")

        assert get_session_result.http_status_code == 200, f"Expected HttpStatusCode 200, got {get_session_result.http_status_code}"
        assert get_session_result.code == "ok", f"Expected Code 'ok', got '{get_session_result.code}'"
        assert get_session_result.success, "Expected Success to be True"

        # Validate Data field
        assert get_session_result.data is not None, "Data field should not be None"
        assert get_session_result.data.session_id == session_id, f"Expected SessionID {session_id}, got {get_session_result.data.session_id}"
        assert get_session_result.data.success, "Expected Data.success to be True"
        assert get_session_result.data.app_instance_id, "AppInstanceID should not be empty"
        print(f"AppInstanceID: {get_session_result.data.app_instance_id}")
        assert get_session_result.data.resource_id, "ResourceID should not be empty"
        print(f"ResourceID: {get_session_result.data.resource_id}")

        print("GetSession API test passed successfully")

    finally:
        # Clean up: Delete the session
        print("Cleaning up: Deleting the session...")
        delete_result = session.delete()
        if delete_result.success:
            print(f"Session {session_id} deleted successfully")
        else:
            print(f"Warning: Failed to delete session: {delete_result.error_message}")


if __name__ == "__main__":
    test_get_session_api()

