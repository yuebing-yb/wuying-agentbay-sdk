package agentbay_test

import (
	"fmt"
	"sync"
	"testing"
	"time"

	mcp "github.com/aliyun/wuying-agentbay-sdk/golang/api/client"
	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay/filesystem"
	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay/models"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
)

// MockWsSession implements both the FileSystem.Session interface and the
// wsProvider optional interface so that WatchDirectory can attempt WS push.
type MockWsSession struct {
	mock.Mock
}

func (m *MockWsSession) GetAPIKey() string {
	args := m.Called()
	return args.String(0)
}

func (m *MockWsSession) GetClient() *mcp.Client {
	args := m.Called()
	if args.Get(0) == nil {
		return nil
	}
	return args.Get(0).(*mcp.Client)
}

func (m *MockWsSession) GetSessionId() string {
	args := m.Called()
	return args.String(0)
}

func (m *MockWsSession) CallMcpTool(toolName string, args interface{}) (*models.McpToolResult, error) {
	mockArgs := m.Called(toolName, args)
	return mockArgs.Get(0).(*models.McpToolResult), mockArgs.Error(1)
}

func (m *MockWsSession) GetWsUrl() string {
	args := m.Called()
	return args.String(0)
}

func (m *MockWsSession) GetToken() string {
	args := m.Called()
	return args.String(0)
}

func (m *MockWsSession) GetWsClient() (interface{}, error) {
	args := m.Called()
	return args.Get(0), args.Error(1)
}

func (m *MockWsSession) GetMcpServerForTool(toolName string) string {
	args := m.Called(toolName)
	return args.String(0)
}

// Logger interface stubs
func (m *MockWsSession) LogInfo(msg string)  {}
func (m *MockWsSession) LogDebug(msg string) {}
func (m *MockWsSession) LogWarn(msg string)  {}
func (m *MockWsSession) LogError(msg string) {}

// TestWsPush_FallsBackToPollingWhenNoWsUrl verifies that when WsUrl is empty,
// WatchDirectory falls back to polling mode.
func TestWsPush_FallsBackToPollingWhenNoWsUrl(t *testing.T) {
	sess := new(MockWsSession)
	fs := filesystem.NewFileSystem(sess)

	sess.On("GetWsUrl").Return("")
	sess.On("GetToken").Return("test-token")
	sess.On("GetMcpServerForTool", "get_file_change").Return("wuying_filesystem")

	pollCount := 0
	var mu sync.Mutex
	sess.On("CallMcpTool", "get_file_change", map[string]string{"path": "/tmp/poll"}).
		Return(&models.McpToolResult{Success: true, Data: "[]"}, nil).
		Run(func(args mock.Arguments) {
			mu.Lock()
			pollCount++
			mu.Unlock()
		})

	stopCh := make(chan struct{})
	wg, readyCh := fs.WatchDirectory("/tmp/poll", func([]*filesystem.FileChangeEvent) {}, 50*time.Millisecond, stopCh)
	<-readyCh

	time.Sleep(150 * time.Millisecond)
	close(stopCh)
	wg.Wait()

	mu.Lock()
	assert.GreaterOrEqual(t, pollCount, 2, "Should have polled at least twice (baseline + ticker)")
	mu.Unlock()
}

// TestWsPush_FallsBackToPollingWhenNoServerName verifies that when
// GetMcpServerForTool returns empty, WatchDirectory falls back to polling.
func TestWsPush_FallsBackToPollingWhenNoServerName(t *testing.T) {
	sess := new(MockWsSession)
	fs := filesystem.NewFileSystem(sess)

	sess.On("GetWsUrl").Return("wss://test.example.com/ws")
	sess.On("GetToken").Return("test-token")
	sess.On("GetMcpServerForTool", "get_file_change").Return("")

	pollCount := 0
	var mu sync.Mutex
	sess.On("CallMcpTool", "get_file_change", map[string]string{"path": "/tmp/poll"}).
		Return(&models.McpToolResult{Success: true, Data: "[]"}, nil).
		Run(func(args mock.Arguments) {
			mu.Lock()
			pollCount++
			mu.Unlock()
		})

	stopCh := make(chan struct{})
	wg, readyCh := fs.WatchDirectory("/tmp/poll", func([]*filesystem.FileChangeEvent) {}, 50*time.Millisecond, stopCh)
	<-readyCh

	time.Sleep(150 * time.Millisecond)
	close(stopCh)
	wg.Wait()

	mu.Lock()
	assert.GreaterOrEqual(t, pollCount, 2, "Should have polled at least twice")
	mu.Unlock()
}

// TestWsPush_FallsBackToPollingOnGetWsClientError verifies that when
// GetWsClient returns an error, WatchDirectory falls back to polling.
func TestWsPush_FallsBackToPollingOnGetWsClientError(t *testing.T) {
	sess := new(MockWsSession)
	fs := filesystem.NewFileSystem(sess)

	sess.On("GetWsUrl").Return("wss://test.example.com/ws")
	sess.On("GetToken").Return("test-token")
	sess.On("GetMcpServerForTool", "get_file_change").Return("wuying_filesystem")
	sess.On("GetWsClient").Return(nil, fmt.Errorf("connection refused"))

	pollCount := 0
	var mu sync.Mutex
	sess.On("CallMcpTool", "get_file_change", map[string]string{"path": "/tmp/poll"}).
		Return(&models.McpToolResult{Success: true, Data: "[]"}, nil).
		Run(func(args mock.Arguments) {
			mu.Lock()
			pollCount++
			mu.Unlock()
		})

	stopCh := make(chan struct{})
	wg, readyCh := fs.WatchDirectory("/tmp/poll", func([]*filesystem.FileChangeEvent) {}, 50*time.Millisecond, stopCh)
	<-readyCh

	time.Sleep(200 * time.Millisecond)
	close(stopCh)
	wg.Wait()

	mu.Lock()
	assert.GreaterOrEqual(t, pollCount, 2, "Should have polled in fallback mode")
	mu.Unlock()
}

// TestWsPush_ExistingPollingTestStillWorks ensures the old polling-only mock
// session (without wsProvider) continues to work.
func TestWsPush_ExistingPollingTestStillWorks(t *testing.T) {
	oldSess := new(MockWatchSession)
	fs := filesystem.NewFileSystem(oldSess)

	callbackCalled := false
	var mu sync.Mutex
	callback := func(events []*filesystem.FileChangeEvent) {
		mu.Lock()
		callbackCalled = true
		mu.Unlock()
	}

	oldSess.On("CallMcpTool", "get_file_change", map[string]string{"path": "/tmp/old"}).
		Return(&models.McpToolResult{
			Success: true,
			Data:    `[{"eventType":"create","path":"/tmp/old/f.txt","pathType":"file"}]`,
		}, nil)

	stopCh := make(chan struct{})
	wg, readyCh := fs.WatchDirectory("/tmp/old", callback, 50*time.Millisecond, stopCh)
	<-readyCh

	time.Sleep(120 * time.Millisecond)
	close(stopCh)
	wg.Wait()

	mu.Lock()
	assert.True(t, callbackCalled, "Callback should have been called in polling mode")
	mu.Unlock()
}
