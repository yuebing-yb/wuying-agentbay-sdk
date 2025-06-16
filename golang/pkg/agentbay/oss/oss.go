package oss

import (
	"encoding/json"
	"fmt"

	"github.com/alibabacloud-go/tea/tea"
	mcp "github.com/aliyun/wuying-agentbay-sdk/golang/api/client"
)

// Oss handles Object Storage Service operations in the AgentBay cloud environment.
type Oss struct {
	Session interface {
		GetAPIKey() string
		GetClient() *mcp.Client
		GetSessionId() string
	}
}

// NewOss creates a new Oss object.
func NewOss(session interface {
	GetAPIKey() string
	GetClient() *mcp.Client
	GetSessionId() string
}) *Oss {
	return &Oss{
		Session: session,
	}
}

// EnvInit creates and initializes OSS environment variables with the specified credentials.
func (o *Oss) EnvInit(accessKeyId, accessKeySecret, securityToken, endpoint, region string) (string, error) {
	// Prepare arguments for the oss_env_init tool
	args := map[string]interface{}{
		"access_key_id":     accessKeyId,
		"access_key_secret": accessKeySecret,
		"security_token":    securityToken,
	}

	// Add optional parameters if provided
	if endpoint != "" {
		args["endpoint"] = endpoint
	}
	if region != "" {
		args["region"] = region
	}

	argsJSON, err := json.Marshal(args)
	if err != nil {
		return "", fmt.Errorf("failed to marshal args: %w", err)
	}

	callToolRequest := &mcp.CallMcpToolRequest{
		Authorization: tea.String("Bearer " + o.Session.GetAPIKey()),
		SessionId:     tea.String(o.Session.GetSessionId()),
		Name:          tea.String("oss_env_init"),
		Args:          tea.String(string(argsJSON)),
	}

	// Log API request
	fmt.Println("API Call: CallMcpTool - oss_env_init")
	fmt.Printf("Request: SessionId=%s\n", *callToolRequest.SessionId)

	response, err := o.Session.GetClient().CallMcpTool(callToolRequest)

	// Log API response
	if err != nil {
		fmt.Println("Error calling CallMcpTool - oss_env_init:", err)
		return "", fmt.Errorf("failed to initialize OSS environment: %w", err)
	}
	if response != nil && response.Body != nil {
		fmt.Println("Response from CallMcpTool - oss_env_init:", response.Body)
	}

	// Convert interface{} to map
	data, ok := response.Body.Data.(map[string]interface{})
	if !ok {
		return "", fmt.Errorf("invalid response data format")
	}

	// Get result field
	result, ok := data["result"].(string)
	if !ok {
		return "", fmt.Errorf("result field not found or not a string")
	}

	return result, nil
}

// Upload uploads a local file or directory to OSS.
func (o *Oss) Upload(bucket, object, path string) (string, error) {
	// Prepare arguments for the oss_upload tool
	args := map[string]interface{}{
		"bucket": bucket,
		"object": object,
		"path":   path,
	}

	argsJSON, err := json.Marshal(args)
	if err != nil {
		return "", fmt.Errorf("failed to marshal args: %w", err)
	}

	callToolRequest := &mcp.CallMcpToolRequest{
		Authorization: tea.String("Bearer " + o.Session.GetAPIKey()),
		SessionId:     tea.String(o.Session.GetSessionId()),
		Name:          tea.String("oss_upload"),
		Args:          tea.String(string(argsJSON)),
	}

	// Log API request
	fmt.Println("API Call: CallMcpTool - oss_upload")
	fmt.Printf("Request: SessionId=%s, Bucket=%s, Object=%s, Path=%s\n",
		*callToolRequest.SessionId, bucket, object, path)

	response, err := o.Session.GetClient().CallMcpTool(callToolRequest)

	// Log API response
	if err != nil {
		fmt.Println("Error calling CallMcpTool - oss_upload:", err)
		return "", fmt.Errorf("failed to upload to OSS: %w", err)
	}
	if response != nil && response.Body != nil {
		fmt.Println("Response from CallMcpTool - oss_upload:", response.Body)
	}

	// Convert interface{} to map
	data, ok := response.Body.Data.(map[string]interface{})
	if !ok {
		return "", fmt.Errorf("invalid response data format")
	}

	// Get result field
	result, ok := data["result"].(string)
	if !ok {
		return "", fmt.Errorf("result field not found or not a string")
	}

	return result, nil
}

// UploadAnonymous uploads a local file or directory to a URL anonymously.
func (o *Oss) UploadAnonymous(url, path string) (string, error) {
	// Prepare arguments for the oss_upload_annon tool
	args := map[string]interface{}{
		"url":  url,
		"path": path,
	}

	argsJSON, err := json.Marshal(args)
	if err != nil {
		return "", fmt.Errorf("failed to marshal args: %w", err)
	}

	callToolRequest := &mcp.CallMcpToolRequest{
		Authorization: tea.String("Bearer " + o.Session.GetAPIKey()),
		SessionId:     tea.String(o.Session.GetSessionId()),
		Name:          tea.String("oss_upload_annon"),
		Args:          tea.String(string(argsJSON)),
	}

	// Log API request
	fmt.Println("API Call: CallMcpTool - oss_upload_annon")
	fmt.Printf("Request: SessionId=%s, URL=%s, Path=%s\n",
		*callToolRequest.SessionId, url, path)

	response, err := o.Session.GetClient().CallMcpTool(callToolRequest)

	// Log API response
	if err != nil {
		fmt.Println("Error calling CallMcpTool - oss_upload_annon:", err)
		return "", fmt.Errorf("failed to upload anonymously: %w", err)
	}
	if response != nil && response.Body != nil {
		fmt.Println("Response from CallMcpTool - oss_upload_annon:", response.Body)
	}

	// Convert interface{} to map
	data, ok := response.Body.Data.(map[string]interface{})
	if !ok {
		return "", fmt.Errorf("invalid response data format")
	}

	// Get result field
	result, ok := data["result"].(string)
	if !ok {
		return "", fmt.Errorf("result field not found or not a string")
	}

	return result, nil
}

// Download downloads an object from OSS to a local file.
func (o *Oss) Download(bucket, object, path string) (string, error) {
	// Prepare arguments for the oss_download tool
	args := map[string]interface{}{
		"bucket": bucket,
		"object": object,
		"path":   path,
	}

	argsJSON, err := json.Marshal(args)
	if err != nil {
		return "", fmt.Errorf("failed to marshal args: %w", err)
	}

	callToolRequest := &mcp.CallMcpToolRequest{
		Authorization: tea.String("Bearer " + o.Session.GetAPIKey()),
		SessionId:     tea.String(o.Session.GetSessionId()),
		Name:          tea.String("oss_download"),
		Args:          tea.String(string(argsJSON)),
	}

	// Log API request
	fmt.Println("API Call: CallMcpTool - oss_download")
	fmt.Printf("Request: SessionId=%s, Bucket=%s, Object=%s, Path=%s\n",
		*callToolRequest.SessionId, bucket, object, path)

	response, err := o.Session.GetClient().CallMcpTool(callToolRequest)

	// Log API response
	if err != nil {
		fmt.Println("Error calling CallMcpTool - oss_download:", err)
		return "", fmt.Errorf("failed to download from OSS: %w", err)
	}
	if response != nil && response.Body != nil {
		fmt.Println("Response from CallMcpTool - oss_download:", response.Body)
	}

	// Convert interface{} to map
	data, ok := response.Body.Data.(map[string]interface{})
	if !ok {
		return "", fmt.Errorf("invalid response data format")
	}

	// Get result field
	result, ok := data["result"].(string)
	if !ok {
		return "", fmt.Errorf("result field not found or not a string")
	}

	return result, nil
}

// DownloadAnonymous downloads a file from a URL anonymously to a local file.
func (o *Oss) DownloadAnonymous(url, path string) (string, error) {
	// Prepare arguments for the oss_download_annon tool
	args := map[string]interface{}{
		"url":  url,
		"path": path,
	}

	argsJSON, err := json.Marshal(args)
	if err != nil {
		return "", fmt.Errorf("failed to marshal args: %w", err)
	}

	callToolRequest := &mcp.CallMcpToolRequest{
		Authorization: tea.String("Bearer " + o.Session.GetAPIKey()),
		SessionId:     tea.String(o.Session.GetSessionId()),
		Name:          tea.String("oss_download_annon"),
		Args:          tea.String(string(argsJSON)),
	}

	// Log API request
	fmt.Println("API Call: CallMcpTool - oss_download_annon")
	fmt.Printf("Request: SessionId=%s, URL=%s, Path=%s\n",
		*callToolRequest.SessionId, url, path)

	response, err := o.Session.GetClient().CallMcpTool(callToolRequest)

	// Log API response
	if err != nil {
		fmt.Println("Error calling CallMcpTool - oss_download_annon:", err)
		return "", fmt.Errorf("failed to download anonymously: %w", err)
	}
	if response != nil && response.Body != nil {
		fmt.Println("Response from CallMcpTool - oss_download_annon:", response.Body)
	}

	// Convert interface{} to map
	data, ok := response.Body.Data.(map[string]interface{})
	if !ok {
		return "", fmt.Errorf("invalid response data format")
	}

	// Get result field
	result, ok := data["result"].(string)
	if !ok {
		return "", fmt.Errorf("result field not found or not a string")
	}

	return result, nil
}
