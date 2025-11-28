package agentbay

import (
	"bytes"
	"crypto/rand"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"time"

	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay/models"
)

// MobileSimulateUploadResult represents the result of uploading mobile info
type MobileSimulateUploadResult struct {
	Success                 bool
	MobileSimulateContextID string
	ErrorMessage            string
}

// MobileSimulateService provides methods to manage persistent mobile dev info and sync to the mobile device
type MobileSimulateService struct {
	agentBay           *AgentBay
	contextService     *ContextService
	simulateEnable     bool
	simulateMode       models.MobileSimulateMode
	contextID          string
	contextSync        *ContextSync
	mobileDevInfoPath  string
	useInternalContext bool
}

// NewMobileSimulateService creates a new MobileSimulateService instance
func NewMobileSimulateService(agentBay *AgentBay) (*MobileSimulateService, error) {
	if agentBay == nil {
		return nil, fmt.Errorf("agentBay is required")
	}
	if agentBay.Context == nil {
		return nil, fmt.Errorf("agentBay.Context is required")
	}

	return &MobileSimulateService{
		agentBay:           agentBay,
		contextService:     agentBay.Context,
		simulateEnable:     false,
		simulateMode:       models.MobileSimulateModePropertiesOnly,
		useInternalContext: true,
	}, nil
}

// SetSimulateEnable sets the simulate enable flag
func (m *MobileSimulateService) SetSimulateEnable(enable bool) {
	m.simulateEnable = enable
}

// GetSimulateEnable gets the simulate enable flag
func (m *MobileSimulateService) GetSimulateEnable() bool {
	return m.simulateEnable
}

// SetSimulateMode sets the simulate mode
// mode: The simulate mode
//   - PropertiesOnly: Simulate only device properties
//   - SensorsOnly: Simulate only device sensors
//   - PackagesOnly: Simulate only installed packages
//   - ServicesOnly: Simulate only system services
//   - All: Simulate all aspects of the device
func (m *MobileSimulateService) SetSimulateMode(mode models.MobileSimulateMode) {
	m.simulateMode = mode
}

// GetSimulateMode gets the simulate mode
func (m *MobileSimulateService) GetSimulateMode() models.MobileSimulateMode {
	return m.simulateMode
}

// SetSimulateContextID sets a previously saved simulate context id
// Please make sure the context id is provided by MobileSimulateService but not user side created context
func (m *MobileSimulateService) SetSimulateContextID(contextID string) {
	m.contextID = contextID
	m.updateContext(true, contextID, nil)
}

// GetSimulateContextID gets the simulate context id
func (m *MobileSimulateService) GetSimulateContextID() string {
	return m.contextID
}

// GetSimulateConfig gets the simulate config
// Returns:
//   - MobileSimulateConfig: The simulate config
//   - Simulate: The simulate feature enable flag
//   - SimulatePath: The path of the mobile dev info file
//   - SimulateMode: The simulate mode
//   - SimulatedContextID: The context ID of the mobile info
func (m *MobileSimulateService) GetSimulateConfig() *models.MobileSimulateConfig {
	var simulatedContextID string
	if m.useInternalContext {
		simulatedContextID = m.contextID
	} else {
		simulatedContextID = ""
	}

	return &models.MobileSimulateConfig{
		Simulate:           m.simulateEnable,
		SimulatePath:       m.mobileDevInfoPath,
		SimulateMode:       m.simulateMode,
		SimulatedContextID: simulatedContextID,
	}
}

// HasMobileInfo checks if the mobile dev info file exists in one context sync
// (Only for user provided context sync)
//
// Args:
//   - contextSync: The context sync to check
//
// Returns:
//   - bool: True if the mobile dev info file exists, False otherwise
//   - error: Error if the operation failed
//
// Notes:
//
//	This method can only be used when mobile simulate context sync is managed by user side.
//	For internal mobile simulate context sync, this method will not work.
func (m *MobileSimulateService) HasMobileInfo(contextSync *ContextSync) (bool, error) {
	if contextSync == nil {
		return false, fmt.Errorf("contextSync is required")
	}
	if contextSync.ContextID == "" {
		return false, fmt.Errorf("contextSync.ContextID is required")
	}
	if contextSync.Path == "" {
		return false, fmt.Errorf("contextSync.Path is required")
	}

	mobileDevInfoPath := contextSync.Path + MobileInfoSubPath
	result, err := m.contextService.ListFiles(contextSync.ContextID, mobileDevInfoPath, 1, 50)

	if err != nil {
		return false, fmt.Errorf("failed to list files: %v", err)
	}
	if !result.Success {
		return false, fmt.Errorf("failed to list files: %s", result.ErrorMessage)
	}

	foundDevInfo := false
	for _, entry := range result.Entries {
		if entry.FileName == MobileInfoFileName {
			foundDevInfo = true
			break
		}
	}

	if foundDevInfo {
		m.updateContext(false, contextSync.ContextID, contextSync)
		return true, nil
	}

	return false, nil
}

// UploadMobileInfo uploads the mobile simulate dev info
//
// Args:
//   - mobileDevInfoContent: The mobile simulate dev info content to upload
//   - contextSync: Optional
//   - If not provided, a new context sync will be created for the mobile simulate service and this context id will
//     return by the MobileSimulateUploadResult. User can use this context id to do persistent mobile simulate across sessions.
//   - If provided, the mobile simulate dev info will be uploaded to the context sync in a specific path.
//
// Returns:
//   - MobileSimulateUploadResult: The result of the upload operation
//   - Success: Whether the operation was successful
//   - MobileSimulateContextID: The context ID of the mobile info
//   - ErrorMessage: The error message if the operation failed
//
// Notes:
//
//	If context_sync is not provided, a new context sync will be created for the mobile simulate.
//	If context_sync is provided, the mobile simulate dev info will be uploaded to the context sync.
//	If the mobile simulate dev info already exists in the context sync, the context sync will be updated.
//	If the mobile simulate dev info does not exist in the context sync, the context sync will be created.
//	If the upload operation fails, the error message will be returned.
func (m *MobileSimulateService) UploadMobileInfo(mobileDevInfoContent string, contextSync *ContextSync) *MobileSimulateUploadResult {
	if mobileDevInfoContent == "" {
		return &MobileSimulateUploadResult{
			Success:      false,
			ErrorMessage: "mobileDevInfoContent is required",
		}
	}

	var jsonData interface{}
	if err := json.Unmarshal([]byte(mobileDevInfoContent), &jsonData); err != nil {
		return &MobileSimulateUploadResult{
			Success:      false,
			ErrorMessage: fmt.Sprintf("mobileDevInfoContent is not a valid JSON string: %v", err),
		}
	}

	// Create context for simulate if not provided
	if contextSync == nil {
		createdContext, err := m.createContextForSimulate()
		if err != nil {
			return &MobileSimulateUploadResult{
				Success:      false,
				ErrorMessage: fmt.Sprintf("Failed to create context for simulate: %v", err),
			}
		}
		m.updateContext(true, createdContext.ID, nil)
	} else {
		if contextSync.ContextID == "" {
			return &MobileSimulateUploadResult{
				Success:      false,
				ErrorMessage: "contextSync.ContextID is required",
			}
		}
		m.updateContext(false, contextSync.ContextID, contextSync)
	}

	uploadPath := m.mobileDevInfoPath + "/" + MobileInfoFileName
	uploadURLResult, err := m.contextService.GetFileUploadUrl(m.contextID, uploadPath)
	if err != nil {
		return &MobileSimulateUploadResult{
			Success:      false,
			ErrorMessage: fmt.Sprintf("Failed to get file upload URL: %v", err),
		}
	}
	if !uploadURLResult.Success {
		return &MobileSimulateUploadResult{
			Success:      false,
			ErrorMessage: fmt.Sprintf("Failed to get file upload URL: %s", uploadURLResult.ErrorMessage),
		}
	}

	importBytes := []byte(mobileDevInfoContent)
	req, err := http.NewRequest("PUT", uploadURLResult.Url, bytes.NewReader(importBytes))
	if err != nil {
		return &MobileSimulateUploadResult{
			Success:      false,
			ErrorMessage: fmt.Sprintf("Failed to create upload request: %v", err),
		}
	}
	req.ContentLength = int64(len(importBytes))
	req.GetBody = func() (io.ReadCloser, error) {
		return io.NopCloser(bytes.NewReader(importBytes)), nil
	}

	client := &http.Client{Timeout: 30 * time.Second}
	resp, err := client.Do(req)
	if err != nil {
		return &MobileSimulateUploadResult{
			Success:      false,
			ErrorMessage: fmt.Sprintf("An error occurred while uploading the file: %v", err),
		}
	}
	defer resp.Body.Close()

	if resp.StatusCode < 200 || resp.StatusCode >= 300 {
		return &MobileSimulateUploadResult{
			Success:      false,
			ErrorMessage: fmt.Sprintf("Upload failed with status code: %d", resp.StatusCode),
		}
	}

	return &MobileSimulateUploadResult{
		Success:                 true,
		MobileSimulateContextID: m.contextID,
	}
}

// updateContext updates the context information
func (m *MobileSimulateService) updateContext(isInternal bool, contextID string, contextSync *ContextSync) {
	if !isInternal {
		if contextSync == nil {
			panic("contextSync is required for external context")
		}
		// Add mobile info path to context sync bw list
		if contextSync.Policy != nil && contextSync.Policy.BWList != nil && contextSync.Policy.BWList.WhiteLists != nil {
			found := false
			for _, whiteList := range contextSync.Policy.BWList.WhiteLists {
				if whiteList.Path == MobileInfoSubPath {
					found = true
					break
				}
			}
			if !found {
				contextSync.Policy.BWList.WhiteLists = append(contextSync.Policy.BWList.WhiteLists, &WhiteList{
					Path:         MobileInfoSubPath,
					ExcludePaths: []string{},
				})
			}
		}
	}

	m.useInternalContext = isInternal
	m.contextID = contextID
	m.contextSync = contextSync
	if isInternal {
		m.mobileDevInfoPath = MobileInfoDefaultPath
	} else {
		m.mobileDevInfoPath = contextSync.Path + MobileInfoSubPath
	}
}

// createContextForSimulate creates a context for simulate
func (m *MobileSimulateService) createContextForSimulate() (*Context, error) {
	randomBytes := make([]byte, 16)
	rand.Read(randomBytes)
	randomHex := hex.EncodeToString(randomBytes)
	contextName := fmt.Sprintf("mobile_sim_%s_%d", randomHex, time.Now().Unix())

	contextResult, err := m.contextService.Get(contextName, true)
	if err != nil {
		return nil, fmt.Errorf("Failed to create mobile simulate context: %v", err)
	}
	if !contextResult.Success || contextResult.Context == nil {
		return nil, fmt.Errorf("Failed to create mobile simulate context: %s", contextResult.ErrorMessage)
	}

	context := contextResult.Context
	return context, nil
}
