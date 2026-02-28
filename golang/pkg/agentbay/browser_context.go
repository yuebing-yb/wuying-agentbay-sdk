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

// BrowserSyncMode controls the scope of browser data synchronization.
type BrowserSyncMode string

const (
	// BrowserSyncModeMinimal synchronizes only essential files (Cookies, Local State).
	// Smallest footprint. Sufficient for basic cookie-based auth.
	BrowserSyncModeMinimal BrowserSyncMode = "minimal"

	// BrowserSyncModeStandard synchronizes login state and anti-risk-control data.
	// Includes Cookies, localStorage, IndexedDB, saved passwords,
	// preferences, HSTS, GPU cache, etc. Recommended for most scenarios.
	BrowserSyncModeStandard BrowserSyncMode = "standard"
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

	// SyncMode controls the scope of browser data synchronization.
	// Defaults to BrowserSyncModeStandard.
	SyncMode BrowserSyncMode
}

// NewBrowserContext creates a BrowserContext with AutoUpload enabled
// and SyncMode set to BrowserSyncModeStandard by default.
func NewBrowserContext(contextID string) *BrowserContext {
	return &BrowserContext{
		ContextID:  contextID,
		AutoUpload: true,
		SyncMode:   BrowserSyncModeStandard,
	}
}

// WithAutoUpload sets AutoUpload and returns the same BrowserContext for chaining.
func (bc *BrowserContext) WithAutoUpload(autoUpload bool) *BrowserContext {
	bc.AutoUpload = autoUpload
	return bc
}

// WithSyncMode sets SyncMode and returns the same BrowserContext for chaining.
func (bc *BrowserContext) WithSyncMode(mode BrowserSyncMode) *BrowserContext {
	bc.SyncMode = mode
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

	var whitelists []*WhiteList

	if bc.SyncMode == BrowserSyncModeMinimal {
		// MINIMAL mode: only Cookies + Local State
		whitelists = []*WhiteList{
			{Path: "/Local State", ExcludePaths: []string{}},
			{Path: "/Default/Cookies", ExcludePaths: []string{}},
			{Path: "/Default/Cookies-journal", ExcludePaths: []string{}},
		}
	} else {
		// STANDARD mode: login state + anti-risk-control data
		whitelists = []*WhiteList{
			// Auth core
			{Path: "/Local State", ExcludePaths: []string{}},
			{Path: "/Default/Cookies", ExcludePaths: []string{}},
			{Path: "/Default/Cookies-journal", ExcludePaths: []string{}},
			// Anti-risk-control device fingerprint (localStorage / IndexedDB)
			{Path: "/Default/Local Storage", ExcludePaths: []string{}},
			{Path: "/Default/IndexedDB", ExcludePaths: []string{}},
			{Path: "/Default/Session Storage", ExcludePaths: []string{}},
			// Saved passwords and form autofill
			{Path: "/Default/Login Data", ExcludePaths: []string{}},
			{Path: "/Default/Login Data-journal", ExcludePaths: []string{}},
			{Path: "/Default/Login Data For Account", ExcludePaths: []string{}},
			{Path: "/Default/Login Data For Account-journal", ExcludePaths: []string{}},
			{Path: "/Default/Web Data", ExcludePaths: []string{}},
			{Path: "/Default/Web Data-journal", ExcludePaths: []string{}},
			// Browser settings and permission consistency
			{Path: "/Default/Preferences", ExcludePaths: []string{}},
			{Path: "/Default/Secure Preferences", ExcludePaths: []string{}},
			// Network behavior consistency (HSTS / QUIC)
			{Path: "/Default/TransportSecurity", ExcludePaths: []string{}},
			{Path: "/Default/Network Persistent State", ExcludePaths: []string{}},
			// Rendering fingerprint stability
			{Path: "/Default/GPUCache", ExcludePaths: []string{}},
			// Cross-domain password matching
			{Path: "/Default/Affiliation Database", ExcludePaths: []string{}},
			{Path: "/Default/Affiliation Database-journal", ExcludePaths: []string{}},
		}
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


