import os
import pytest
from agentbay import AgentBay, CreateSessionParams
from agentbay.context_sync import ContextSync, SyncPolicy, UploadPolicy, DownloadPolicy, DeletePolicy, ExtractPolicy, RecyclePolicy, BWList, WhiteList, UploadMode
from agentbay.session import Session
import time
import random

@pytest.fixture(scope="module")
def agentbay_client():
    """Initialize AgentBay client with API key from environment."""
    api_key = os.getenv("AGENTBAY_API_KEY")
    if not api_key:
        print("Warning: AGENTBAY_API_KEY environment variable not set. Using default test key.")
        api_key = "akm-xxx"  # Replace with your test API key
    return AgentBay(api_key=api_key)

def generate_unique_id():
    """Generate unique ID for test isolation."""
    timestamp = int(time.time() * 1000000) + random.randint(0, 999)
    random_part = random.randint(0, 9999)
    return f"{timestamp}-{random_part}"

class TestContextSyncUploadModeIntegration:
    """Context Sync Upload Mode Integration Tests"""
    
    @classmethod
    def setup_class(cls):
        """Setup test class with unique ID and session tracking."""
        cls.unique_id = generate_unique_id()
        cls.test_sessions = []
        print(f"Using unique ID for test: {cls.unique_id}")

    @classmethod
    def teardown_class(cls):
        """Cleanup all test sessions."""
        print("Cleaning up: Deleting all test sessions...")
        # Note: Sessions should be cleaned up in individual tests
        # This is a safety net for any remaining sessions

    def test_create_session_with_default_file_upload_mode(self, agentbay_client: AgentBay):
        """Test creating session with default File upload mode and write file."""
        print("\n=== Testing basic functionality with default File upload mode ===")

        # Step 1: Use context.get method to generate contextId
        context_name = f"test-context-{self.unique_id}"
        print(f"Creating context with name: {context_name}")
        
        context_result = agentbay_client.context.get(context_name, True)
        assert context_result.success, f"Failed to create context: {context_result.error_message}"
        assert context_result.context_id is not None
        assert context_result.context_id != ""
        
        print(f"Generated contextId: {context_result.context_id}")
        print(f"Context get request ID: {context_result.request_id}")

        # Step 2: Create session with contextSync using default File uploadMode
        sync_policy = SyncPolicy.default()  # Uses default uploadMode "File"

        context_sync = ContextSync(
            context_id=context_result.context_id,
            path="/tmp/test",
            policy=sync_policy
        )

        session_params = CreateSessionParams(
            labels={
                "test": f"upload-mode-{self.unique_id}",
                "type": "basic-functionality"
            },
            context_syncs=[context_sync]
        )

        print("Creating session with default File upload mode...")
        session_result = agentbay_client.create(session_params)

        # Step 3: Verify session creation success
        assert session_result.success, f"Failed to create session: {session_result.error_message}"
        assert session_result.session is not None
        assert session_result.request_id is not None
        assert session_result.request_id != ""

        session = session_result.session
        self.test_sessions.append(session)

        print(f"✅ Session created successfully!")
        print(f"Session ID: {session.session_id}")
        print(f"Session creation request ID: {session_result.request_id}")

        # Get session info to verify appInstanceId
        session_info = agentbay_client.get_session(session.session_id)
        assert session_info.success, f"Failed to get session info: {session_info.error_message}"
        assert session_info.data is not None
        
        print(f"App Instance ID: {session_info.data.app_instance_id}")
        print(f"Get session request ID: {session_info.request_id}")

        print("✅ All basic functionality tests passed!")

        # Cleanup
        print("Cleaning up: Deleting the session...")
        delete_result = agentbay_client.delete(session, sync_context=True)
        assert delete_result.success, f"Failed to delete session: {delete_result.error_message}"
        print(f"Session {session.session_id} deleted successfully")
        self.test_sessions.remove(session)

    def test_context_sync_with_archive_mode_and_file_operations(self, agentbay_client: AgentBay):
        """Test contextId and path usage with Archive mode and file operations."""
        print("\n=== Testing contextId and path usage with Archive mode and file operations ===")

        context_name = f"archive-mode-context-{self.unique_id}"
        context_result = agentbay_client.context.get(context_name, True)
        
        assert context_result.success, f"Failed to create context: {context_result.error_message}"
        assert context_result.context_id is not None
        assert context_result.context_id != ""

        print(f"Generated contextId: {context_result.context_id}")

        # Create sync policy with Archive upload mode
        upload_policy = UploadPolicy(upload_mode=UploadMode.ARCHIVE)
        sync_policy = SyncPolicy(upload_policy=upload_policy)

        context_sync = ContextSync.new(
            context_id=context_result.context_id,
            path="/tmp/archive-mode-test",
            policy=sync_policy
        )

        assert context_sync.context_id == context_result.context_id
        assert context_sync.path == "/tmp/archive-mode-test"
        assert context_sync.policy.upload_policy.upload_mode == UploadMode.ARCHIVE

        print("✅ ContextSync.new works correctly with contextId and path using Archive mode")

        # Create session with the contextSync
        session_params = CreateSessionParams(
            labels={
                "test": f"archive-mode-{self.unique_id}",
                "type": "contextId-path-validation"
            },
            context_syncs=[context_sync]
        )

        print("Creating session with Archive mode contextSync...")
        session_result = agentbay_client.create(session_params)

        assert session_result.success, f"Failed to create session: {session_result.error_message}"
        assert session_result.session is not None
        assert session_result.request_id is not None

        session = session_result.session
        self.test_sessions.append(session)

        # Get session info to verify appInstanceId
        session_info = agentbay_client.get_session(session.session_id)
        assert session_info.success, f"Failed to get session info: {session_info.error_message}"
        assert session_info.data is not None
        
        print(f"App Instance ID: {session_info.data.app_instance_id}")

        print(f"✅ Session created successfully with ID: {session.session_id}")
        print(f"Session creation request ID: {session_result.request_id}")

        # Write a 5KB file using FileSystem
        print("Writing 5KB file using FileSystem...")
        
        # Generate 5KB content (approximately 5120 bytes)
        content_size = 5 * 1024  # 5KB
        base_content = "Archive mode test successful! This is a test file created in the session path. "
        repeated_content = base_content * (content_size // len(base_content) + 1)
        file_content = repeated_content[:content_size]
        
        # Create file path in the session path directory
        file_path = "/tmp/archive-mode-test/test-file-5kb.txt"
        
        print(f"Creating file: {file_path}")
        print(f"File content size: {len(file_content)} bytes")

        write_result = session.file_system.write_file(file_path, file_content, "overwrite")

        # Verify file write success
        assert write_result.success, f"Failed to write file: {write_result.error_message}"
        assert write_result.request_id is not None
        assert write_result.request_id != ""

        print(f"✅ File write successful!")
        print(f"Write file request ID: {write_result.request_id}")

        # Test context info functionality
        print("Testing context info functionality...")
        info_result = session.context.info()
        
        assert info_result.success, f"Failed to get context info: {info_result.error_message}"
        assert info_result.request_id is not None
        assert info_result.context_status_data is not None
        
        print(f"✅ Context info successful!")
        print(f"Info request ID: {info_result.request_id}")
        print(f"Context status data count: {len(info_result.context_status_data)}")
        
        # Log context status details
        if len(info_result.context_status_data) > 0:
            print("Context status details:")
            for index, status in enumerate(info_result.context_status_data):
                print(f"  [{index}] ContextId: {status.context_id}, Path: {status.path}, Status: {status.status}, TaskType: {status.task_type}")

        # Get file information
        print("Getting file information...")
        
        file_info_result = session.file_system.get_file_info(file_path)

        # Verify getFileInfo success
        assert file_info_result.success, f"Failed to get file info: {file_info_result.error_message}"
        assert file_info_result.file_info is not None
        assert file_info_result.request_id is not None
        assert file_info_result.request_id != ""

        print(f"✅ Get file info successful!")
        print(f"Get file info request ID: {file_info_result.request_id}")
        print(f"File info: {file_info_result.file_info}")

        # Verify file information
        assert file_info_result.file_info['size'] == content_size
        assert file_info_result.file_info['isDirectory'] == False
        print("✅ Archive mode contextSync with contextId and path works correctly, and file operations completed successfully")

        # Cleanup
        print("Cleaning up: Deleting the session...")
        delete_result = agentbay_client.delete(session, sync_context=True)
        assert delete_result.success, f"Failed to delete session: {delete_result.error_message}"
        print(f"Session {session.session_id} deleted successfully")
        self.test_sessions.remove(session)


    def test_invalid_upload_mode_with_policy_assignment(self, agentbay_client: AgentBay):
        """Test error handling when using invalid uploadMode with policy assignment."""
        print("\n=== Testing invalid uploadMode with policy assignment ===")

        context_name = f"invalid-policy-context-{self.unique_id}"
        context_result = agentbay_client.context.get(context_name, True)
        assert context_result.success, f"Failed to create context: {context_result.error_message}"

        # Test 1: Invalid upload mode through SyncPolicy creation (new test for agentbay.create scenario)
        print("Testing invalid uploadMode through SyncPolicy instantiation (agentbay.create scenario)...")
        
        with pytest.raises(ValueError) as exc_info:
            # This simulates what happens when user passes invalid uploadMode in agentbay.create
            invalid_upload_policy = UploadPolicy(upload_mode="InvalidMode")
            sync_policy = SyncPolicy(upload_policy=invalid_upload_policy)

        assert "Invalid upload_mode value: InvalidMode" in str(exc_info.value)
        assert "Valid values are: File, Archive" in str(exc_info.value)

        print("✅ SyncPolicy correctly threw error for invalid uploadMode during instantiation")

        # Test 2: Test the complete flow with ContextSync (most realistic scenario)
        print("Testing invalid uploadMode through complete ContextSync flow...")
        
        with pytest.raises(ValueError) as exc_info:
            # This is the most realistic scenario - user creates ContextSync with invalid policy
            invalid_upload_policy = UploadPolicy(upload_mode="BadValue")
            sync_policy = SyncPolicy(upload_policy=invalid_upload_policy)
            
            # This would be used in agentbay.create(CreateSessionParams(context_syncs=[context_sync]))
            context_sync = ContextSync.new(
                context_id=context_result.context_id,
                path="/tmp/test-invalid",
                policy=sync_policy
            )

        assert "Invalid upload_mode value: BadValue" in str(exc_info.value)
        assert "Valid values are: File, Archive" in str(exc_info.value)

        print("✅ Complete ContextSync flow correctly threw error for invalid uploadMode")

    def test_valid_upload_mode_values(self, agentbay_client: AgentBay):
        """Test that valid uploadMode values are accepted."""
        print("\n=== Testing valid uploadMode values ===")

        context_name = f"valid-context-{self.unique_id}"
        context_result = agentbay_client.context.get(context_name, True)
        assert context_result.success, f"Failed to create context: {context_result.error_message}"

        # Test "File" mode
        file_upload_policy = UploadPolicy(upload_mode=UploadMode.FILE)
        file_sync_policy = SyncPolicy(upload_policy=file_upload_policy)

        # Should not raise any exception
        file_context_sync = ContextSync.new(
            context_id=context_result.context_id,
            path="/tmp/test-file",
            policy=file_sync_policy
        )
        
        assert file_context_sync.policy.upload_policy.upload_mode == UploadMode.FILE
        print("✅ 'File' uploadMode accepted successfully")

        # Test "Archive" mode
        archive_upload_policy = UploadPolicy(upload_mode=UploadMode.ARCHIVE)
        archive_sync_policy = SyncPolicy(upload_policy=archive_upload_policy)

        # Should not raise any exception
        archive_context_sync = ContextSync.new(
            context_id=context_result.context_id,
            path="/tmp/test-archive",
            policy=archive_sync_policy
        )
        
        assert archive_context_sync.policy.upload_policy.upload_mode == UploadMode.ARCHIVE
        print("✅ 'Archive' uploadMode accepted successfully")

    def test_upload_policy_serialization(self, agentbay_client: AgentBay):
        """Test that UploadPolicy serializes uploadMode correctly."""
        print("\n=== Testing UploadPolicy serialization ===")

        # Test File mode serialization
        file_policy = UploadPolicy(upload_mode=UploadMode.FILE)
        file_dict = file_policy.__dict__()
        
        assert "uploadMode" in file_dict
        assert file_dict["uploadMode"] == "File"
        print("✅ File mode serialization works correctly")

        # Test Archive mode serialization
        archive_policy = UploadPolicy(upload_mode=UploadMode.ARCHIVE)
        archive_dict = archive_policy.__dict__()
        
        assert "uploadMode" in archive_dict
        assert archive_dict["uploadMode"] == "Archive"
        print("✅ Archive mode serialization works correctly")

        # Test default policy serialization
        default_policy = UploadPolicy.default()
        default_dict = default_policy.__dict__()
        
        assert "uploadMode" in default_dict
        assert default_dict["uploadMode"] == "File"  # Default should be File
        print("✅ Default policy serialization works correctly")