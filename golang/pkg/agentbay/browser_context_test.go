package agentbay

import (
	"encoding/json"
	"testing"
)

func TestNewBrowserContext_Defaults(t *testing.T) {
	bc := NewBrowserContext("ctx-123")
	if bc == nil {
		t.Fatalf("expected non-nil BrowserContext")
	}
	if bc.ContextID != "ctx-123" {
		t.Fatalf("expected ContextID ctx-123, got %q", bc.ContextID)
	}
	if bc.AutoUpload != true {
		t.Fatalf("expected default AutoUpload=true, got %v", bc.AutoUpload)
	}
	if bc.SyncMode != BrowserSyncModeStandard {
		t.Fatalf("expected default SyncMode=%q, got %q", BrowserSyncModeStandard, bc.SyncMode)
	}
}

func TestBrowserContext_WithSyncMode(t *testing.T) {
	bc := NewBrowserContext("ctx-456").WithSyncMode(BrowserSyncModeMinimal)
	if bc.SyncMode != BrowserSyncModeMinimal {
		t.Fatalf("expected SyncMode=%q, got %q", BrowserSyncModeMinimal, bc.SyncMode)
	}
}

func TestBuildBrowserContext_StandardMode(t *testing.T) {
	bc := NewBrowserContext("ctx-abc").WithAutoUpload(false)

	item, err := buildBrowserContextPersistenceDataListItem(bc)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if item == nil {
		t.Fatalf("expected non-nil item")
	}
	if item.Path == nil || *item.Path != browserDataPath {
		got := ""
		if item.Path != nil {
			got = *item.Path
		}
		t.Fatalf("expected path %q, got %q", browserDataPath, got)
	}
	if item.ContextId == nil || *item.ContextId != "ctx-abc" {
		got := ""
		if item.ContextId != nil {
			got = *item.ContextId
		}
		t.Fatalf("expected contextId %q, got %q", "ctx-abc", got)
	}
	if item.Policy == nil || *item.Policy == "" {
		t.Fatalf("expected non-empty policy JSON")
	}

	var policy SyncPolicy
	if err := json.Unmarshal([]byte(*item.Policy), &policy); err != nil {
		t.Fatalf("failed to unmarshal policy: %v", err)
	}
	if policy.UploadPolicy == nil {
		t.Fatalf("expected uploadPolicy to be present")
	}
	if policy.UploadPolicy.AutoUpload != false {
		t.Fatalf("expected uploadPolicy.autoUpload=false, got %v", policy.UploadPolicy.AutoUpload)
	}
	if policy.BWList == nil || policy.BWList.WhiteLists == nil {
		t.Fatalf("expected bwList.whiteLists to be present")
	}

	want := map[string]bool{
		"/Local State":                            false,
		"/Default/Cookies":                        false,
		"/Default/Cookies-journal":                false,
		"/Default/Local Storage":                  false,
		"/Default/IndexedDB":                      false,
		"/Default/Session Storage":                false,
		"/Default/Login Data":                     false,
		"/Default/Login Data-journal":             false,
		"/Default/Login Data For Account":         false,
		"/Default/Login Data For Account-journal": false,
		"/Default/Web Data":                       false,
		"/Default/Web Data-journal":               false,
		"/Default/Preferences":                    false,
		"/Default/Secure Preferences":             false,
		"/Default/TransportSecurity":              false,
		"/Default/Network Persistent State":       false,
		"/Default/GPUCache":                       false,
		"/Default/Affiliation Database":           false,
		"/Default/Affiliation Database-journal":   false,
	}
	if len(policy.BWList.WhiteLists) != len(want) {
		t.Fatalf("expected %d whitelist entries in STANDARD mode, got %d", len(want), len(policy.BWList.WhiteLists))
	}
	for _, wl := range policy.BWList.WhiteLists {
		if _, ok := want[wl.Path]; ok {
			want[wl.Path] = true
		}
	}
	for path, found := range want {
		if !found {
			t.Fatalf("expected whitelist path %q to be present", path)
		}
	}
}

func TestBuildBrowserContext_MinimalMode(t *testing.T) {
	bc := NewBrowserContext("ctx-min").WithSyncMode(BrowserSyncModeMinimal)

	item, err := buildBrowserContextPersistenceDataListItem(bc)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}

	var policy SyncPolicy
	if err := json.Unmarshal([]byte(*item.Policy), &policy); err != nil {
		t.Fatalf("failed to unmarshal policy: %v", err)
	}
	if policy.BWList == nil || policy.BWList.WhiteLists == nil {
		t.Fatalf("expected bwList.whiteLists to be present")
	}

	want := map[string]bool{
		"/Local State":             false,
		"/Default/Cookies":         false,
		"/Default/Cookies-journal": false,
	}
	if len(policy.BWList.WhiteLists) != len(want) {
		t.Fatalf("expected %d whitelist entries in MINIMAL mode, got %d", len(want), len(policy.BWList.WhiteLists))
	}
	for _, wl := range policy.BWList.WhiteLists {
		if _, ok := want[wl.Path]; ok {
			want[wl.Path] = true
		}
	}
	for path, found := range want {
		if !found {
			t.Fatalf("expected whitelist path %q to be present", path)
		}
	}
}
