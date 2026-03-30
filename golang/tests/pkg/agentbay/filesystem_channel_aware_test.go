package agentbay_test

import (
	"strings"
	"testing"

	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
	"github.com/aliyun/wuying-agentbay-sdk/golang/tests/pkg/agentbay/testutil"
)

// logChannelInfo logs which channel type the session is using.
func logChannelInfo(t *testing.T, session *agentbay.Session) {
	t.Helper()
	linkUrl := session.GetLinkUrl()
	token := session.GetToken()
	if linkUrl != "" && token != "" {
		t.Logf("[Channel] Using HTTP (LinkUrl) channel")
	} else {
		t.Logf("[Channel] Using MQTT (API) channel")
	}
}

// TestFileSystem_ChannelAware_SmallFile tests write+read of a small file.
func TestFileSystem_ChannelAware_SmallFile(t *testing.T) {
	sessionParams := agentbay.NewCreateSessionParams().WithImageId("linux_latest")
	session, cleanup := testutil.SetupAndCleanup(t, sessionParams)
	defer cleanup()

	if session.FileSystem == nil {
		t.Skip("FileSystem not available")
	}

	logChannelInfo(t, session)

	content := "Hello, channel-aware filesystem!"
	path := TestPathPrefix + "/channel_test_small.txt"

	_, err := session.FileSystem.WriteFile(path, content, "overwrite")
	if err != nil {
		t.Fatalf("WriteFile failed: %v", err)
	}

	readResult, err := session.FileSystem.ReadFile(path)
	if err != nil {
		t.Fatalf("ReadFile failed: %v", err)
	}
	if readResult.Content != content {
		t.Errorf("Content mismatch: expected %d bytes, got %d bytes", len(content), len(readResult.Content))
	}
	t.Logf("[PASS] Small file roundtrip: %d bytes", len(content))
}

// TestFileSystem_ChannelAware_MediumFile tests write+read of a ~60KB file
// (previously required chunking on MQTT channel).
func TestFileSystem_ChannelAware_MediumFile(t *testing.T) {
	sessionParams := agentbay.NewCreateSessionParams().WithImageId("linux_latest")
	session, cleanup := testutil.SetupAndCleanup(t, sessionParams)
	defer cleanup()

	if session.FileSystem == nil {
		t.Skip("FileSystem not available")
	}

	logChannelInfo(t, session)

	content := strings.Repeat("A", 60*1024) // 60KB
	path := TestPathPrefix + "/channel_test_medium.txt"

	_, err := session.FileSystem.WriteFile(path, content, "overwrite")
	if err != nil {
		t.Fatalf("WriteFile failed: %v", err)
	}

	readResult, err := session.FileSystem.ReadFile(path)
	if err != nil {
		t.Fatalf("ReadFile failed: %v", err)
	}
	if readResult.Content != content {
		t.Errorf("Content mismatch: expected %d bytes, got %d bytes", len(content), len(readResult.Content))
	}
	t.Logf("[PASS] Medium file roundtrip: %d bytes", len(content))
}

// TestFileSystem_ChannelAware_LargeFile tests write+read of a ~200KB file
// (previously required multiple chunks on MQTT channel).
func TestFileSystem_ChannelAware_LargeFile(t *testing.T) {
	sessionParams := agentbay.NewCreateSessionParams().WithImageId("linux_latest")
	session, cleanup := testutil.SetupAndCleanup(t, sessionParams)
	defer cleanup()

	if session.FileSystem == nil {
		t.Skip("FileSystem not available")
	}

	logChannelInfo(t, session)

	content := strings.Repeat("B", 200*1024) // 200KB
	path := TestPathPrefix + "/channel_test_large.txt"

	_, err := session.FileSystem.WriteFile(path, content, "overwrite")
	if err != nil {
		t.Fatalf("WriteFile failed: %v", err)
	}

	readResult, err := session.FileSystem.ReadFile(path)
	if err != nil {
		t.Fatalf("ReadFile failed: %v", err)
	}
	if readResult.Content != content {
		t.Errorf("Content mismatch: expected %d bytes, got %d bytes", len(content), len(readResult.Content))
	}
	t.Logf("[PASS] Large file roundtrip: %d bytes", len(content))
}

// TestFileSystem_ChannelAware_AppendMode tests append mode works correctly.
func TestFileSystem_ChannelAware_AppendMode(t *testing.T) {
	sessionParams := agentbay.NewCreateSessionParams().WithImageId("linux_latest")
	session, cleanup := testutil.SetupAndCleanup(t, sessionParams)
	defer cleanup()

	if session.FileSystem == nil {
		t.Skip("FileSystem not available")
	}

	logChannelInfo(t, session)

	path := TestPathPrefix + "/channel_test_append.txt"

	_, err := session.FileSystem.WriteFile(path, "first part", "overwrite")
	if err != nil {
		t.Fatalf("Initial WriteFile failed: %v", err)
	}

	_, err = session.FileSystem.WriteFile(path, " second part", "append")
	if err != nil {
		t.Fatalf("Append WriteFile failed: %v", err)
	}

	readResult, err := session.FileSystem.ReadFile(path)
	if err != nil {
		t.Fatalf("ReadFile failed: %v", err)
	}

	expected := "first part second part"
	if readResult.Content != expected {
		t.Errorf("Append content mismatch: expected %q, got %q", expected, readResult.Content)
	}
	t.Log("[PASS] Append mode works correctly")
}

// TestFileSystem_ChannelAware_UnicodeContent tests write+read of unicode content.
func TestFileSystem_ChannelAware_UnicodeContent(t *testing.T) {
	sessionParams := agentbay.NewCreateSessionParams().WithImageId("linux_latest")
	session, cleanup := testutil.SetupAndCleanup(t, sessionParams)
	defer cleanup()

	if session.FileSystem == nil {
		t.Skip("FileSystem not available")
	}

	logChannelInfo(t, session)

	content := "你好世界 🌍 こんにちは 안녕하세요 مرحبا"
	path := TestPathPrefix + "/channel_test_unicode.txt"

	_, err := session.FileSystem.WriteFile(path, content, "overwrite")
	if err != nil {
		t.Fatalf("WriteFile failed: %v", err)
	}

	readResult, err := session.FileSystem.ReadFile(path)
	if err != nil {
		t.Fatalf("ReadFile failed: %v", err)
	}

	if readResult.Content != content {
		t.Errorf("Unicode content mismatch")
	}
	t.Log("[PASS] Unicode content roundtrip")
}
