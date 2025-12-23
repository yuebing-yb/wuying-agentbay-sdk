package agentbay

import (
	"encoding/json"
	"errors"

	mcp "github.com/aliyun/wuying-agentbay-sdk/golang/api/client"
	"github.com/alibabacloud-go/tea/tea"
)

const (
	// browserDataPath is the path inside the session VM where Chromium persists user data.
	// NOTE: This intentionally matches the path used by the browser module.
	browserDataPath = "/tmp/agentbay_browser"
)

// BrowserContext configures persistent browser state for a session.
//
// This is the Go SDK equivalent of Python's BrowserContext in CreateSessionParams.
// It binds a session to a cloud Context (by ContextID) and controls whether browser data
// is uploaded back to the Context on session release.
type BrowserContext struct {
	// ContextID is the ID of the cloud Context used to persist browser state.
	ContextID string

	// AutoUpload controls whether browser data is uploaded on session end.
	AutoUpload bool
}

// NewBrowserContext creates a BrowserContext with AutoUpload enabled by default.
func NewBrowserContext(contextID string) *BrowserContext {
	return &BrowserContext{
		ContextID:   contextID,
		AutoUpload: true,
	}
}

// WithAutoUpload sets AutoUpload and returns the same BrowserContext for chaining.
func (bc *BrowserContext) WithAutoUpload(autoUpload bool) *BrowserContext {
	bc.AutoUpload = autoUpload
	return bc
}

func buildBrowserContextPersistenceDataListItem(bc *BrowserContext) (*mcp.CreateMcpSessionRequestPersistenceDataList, error) {
	if bc == nil {
		return nil, errors.New("browser context is nil")
	}
	if bc.ContextID == "" {
		return nil, errors.New("browser context_id is required")
	}

	uploadPolicy := NewUploadPolicy()
	uploadPolicy.AutoUpload = bc.AutoUpload

	whitelists := []*WhiteList{
		{Path: "/Local State", ExcludePaths: []string{}},
		{Path: "/Default/Cookies", ExcludePaths: []string{}},
		{Path: "/Default/Cookies-journal", ExcludePaths: []string{}},
	}

	syncPolicy := &SyncPolicy{
		UploadPolicy:  uploadPolicy,
		BWList:        &BWList{WhiteLists: whitelists},
		RecyclePolicy: NewRecyclePolicy(),
	}

	policyJSON, err := json.Marshal(syncPolicy)
	if err != nil {
		return nil, err
	}

	return &mcp.CreateMcpSessionRequestPersistenceDataList{
		ContextId: tea.String(bc.ContextID),
		Path:      tea.String(browserDataPath),
		Policy:    tea.String(string(policyJSON)),
	}, nil
}


