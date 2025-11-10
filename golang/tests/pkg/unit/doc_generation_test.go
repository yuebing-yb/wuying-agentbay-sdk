package agentbay_test

import (
	"bytes"
	"os"
	"os/exec"
	"path/filepath"
	"testing"
)

func TestGenerateGoAPIDocs(t *testing.T) {
	moduleRoot, err := filepath.Abs(filepath.Join("..", "..", ".."))
	if err != nil {
		t.Fatalf("resolve module root: %v", err)
	}

	docsDir := filepath.Join(moduleRoot, "docs", "api")
	if err := os.RemoveAll(docsDir); err != nil {
		t.Fatalf("cleanup docs dir: %v", err)
	}

	cmd := exec.Command("go", "run", "./scripts/generate_api_docs.go")
	cmd.Dir = moduleRoot
	output, err := cmd.CombinedOutput()
	if err != nil {
		t.Fatalf("generate docs failed: %v\n%s", err, string(output))
	}

	target := filepath.Join(docsDir, "common-features", "basics", "session.md")
	data, err := os.ReadFile(target)
	if err != nil {
		t.Fatalf("session doc missing: %v", err)
	}

	if !bytes.Contains(data, []byte("# Session API Reference")) {
		t.Fatalf("session doc missing expected heading")
	}
}
