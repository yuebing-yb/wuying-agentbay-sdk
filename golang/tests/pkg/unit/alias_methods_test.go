package agentbay_test

import (
	"testing"

	mcp "github.com/aliyun/wuying-agentbay-sdk/golang/api/client"
	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay/code"
	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay/command"
	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay/filesystem"
	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay/models"
	"github.com/stretchr/testify/assert"
)

type aliasTestSession struct {
	callMcpToolFunc func(toolName string, args interface{}) (*models.McpToolResult, error)
}

func (s *aliasTestSession) GetAPIKey() string                        { return "test-api-key" }
func (s *aliasTestSession) GetClient() *mcp.Client                   { return nil }
func (s *aliasTestSession) GetSessionId() string                     { return "test-session-id" }
func (s *aliasTestSession) IsVpc() bool                              { return false }
func (s *aliasTestSession) NetworkInterfaceIp() string               { return "" }
func (s *aliasTestSession) HttpPort() string                         { return "" }
func (s *aliasTestSession) CallMcpTool(toolName string, args interface{}) (*models.McpToolResult, error) {
	if s.callMcpToolFunc != nil {
		return s.callMcpToolFunc(toolName, args)
	}
	return &models.McpToolResult{Success: true, Data: "", RequestID: "request-123"}, nil
}

func TestCommand_RunAndExecAliases(t *testing.T) {
	s := &aliasTestSession{}
	s.callMcpToolFunc = func(toolName string, args interface{}) (*models.McpToolResult, error) {
		assert.Equal(t, "shell", toolName)
		m, ok := args.(map[string]interface{})
		assert.True(t, ok)
		assert.Equal(t, "echo test", m["command"])
		assert.Equal(t, 2000, m["timeout_ms"])
		assert.Equal(t, "/tmp", m["cwd"])
		assert.Equal(t, map[string]string{"A": "B"}, m["envs"])
		return &models.McpToolResult{Success: true, Data: "ok", RequestID: "request-123"}, nil
	}

	cmd := command.NewCommand(s)
	_, err := cmd.Run(
		"echo test",
		command.WithTimeoutMs(2000),
		command.WithCwd("/tmp"),
		command.WithEnvs(map[string]string{"A": "B"}),
	)
	assert.NoError(t, err)

	_, err = cmd.Exec(
		"echo test",
		command.WithTimeoutMs(2000),
		command.WithCwd("/tmp"),
		command.WithEnvs(map[string]string{"A": "B"}),
	)
	assert.NoError(t, err)
}

func TestCode_RunAndExecuteAliases(t *testing.T) {
	s := &aliasTestSession{}
	s.callMcpToolFunc = func(toolName string, args interface{}) (*models.McpToolResult, error) {
		assert.Equal(t, "run_code", toolName)
		m, ok := args.(map[string]interface{})
		assert.True(t, ok)
		assert.Equal(t, "print('OK')", m["code"])
		assert.Equal(t, "python", m["language"])
		assert.Equal(t, 10, m["timeout_s"])
		return &models.McpToolResult{Success: true, Data: "OK", RequestID: "request-123"}, nil
	}

	c := code.NewCode(s)
	_, err := c.Run("print('OK')", "python", 10)
	assert.NoError(t, err)
	_, err = c.Execute("print('OK')", "python", 10)
	assert.NoError(t, err)
}

func TestFileSystem_Aliases(t *testing.T) {
	callCount := 0
	fileDeleted := false
	s := &aliasTestSession{}
	s.callMcpToolFunc = func(toolName string, args interface{}) (*models.McpToolResult, error) {
		callCount++
		switch toolName {
		case "list_directory":
			return &models.McpToolResult{Success: true, Data: "[FILE] a.txt", RequestID: "request-123"}, nil
		case "delete_file":
			fileDeleted = true
			return &models.McpToolResult{Success: true, Data: "True", RequestID: "request-123"}, nil
		case "get_file_info":
			// After file is deleted, get_file_info should fail
			if fileDeleted {
				return &models.McpToolResult{Success: false, ErrorMessage: "File not found", RequestID: "request-123"}, nil
			}
			return &models.McpToolResult{Success: true, Data: "size: 0\nisDirectory: false", RequestID: "request-123"}, nil
		case "write_file":
			fileDeleted = false // File is recreated
			return &models.McpToolResult{Success: true, Data: "True", RequestID: "request-123"}, nil
		default:
			return &models.McpToolResult{Success: false, ErrorMessage: "unexpected tool", RequestID: "request-123"}, nil
		}
	}

	fs := filesystem.NewFileSystem(s)

	listRes, err := fs.List("/tmp")
	assert.NoError(t, err)
	assert.Len(t, listRes.Entries, 1)
	assert.Equal(t, "a.txt", listRes.Entries[0].Name)

	_, err = fs.Delete("/tmp/a.txt")
	assert.NoError(t, err)

	_, err = fs.Read("/tmp/a.txt")
	assert.Error(t, err)

	_, err = fs.Write("/tmp/a.txt", "hello", "overwrite")
	assert.NoError(t, err)
	assert.GreaterOrEqual(t, callCount, 4)
}

func TestSession_FsAliases(t *testing.T) {
	fs := &filesystem.FileSystem{}
	s := &agentbay.Session{FileSystem: fs}
	assert.Equal(t, fs, s.Fs())
	assert.Equal(t, fs, s.Filesystem())
	assert.Equal(t, fs, s.Files())
}
