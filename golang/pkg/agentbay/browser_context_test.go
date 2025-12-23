package agentbay

import (
	"encoding/json"
	"testing"
)

func TestNewBrowserContext_DefaultAutoUpload(t *testing.T) {
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
}

func TestBuildBrowserContextPersistenceDataListItem_PolicyShape(t *testing.T) {
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
		"/Local State":             false,
		"/Default/Cookies":         false,
		"/Default/Cookies-journal": false,
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


