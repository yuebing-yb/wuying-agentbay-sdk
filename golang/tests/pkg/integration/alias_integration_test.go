package integration_test

import (
	"strings"
	"testing"

	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
	"github.com/aliyun/wuying-agentbay-sdk/golang/tests/pkg/agentbay/testutil"
)

func TestAliasesIntegration(t *testing.T) {
	apiKey := testutil.GetTestAPIKey(t)
	ab, err := agentbay.NewAgentBay(apiKey)
	if err != nil {
		t.Fatalf("Error initializing AgentBay client: %v", err)
	}

	params := agentbay.NewCreateSessionParams().WithImageId("code_latest")
	sessionResult, err := ab.Create(params)
	if err != nil {
		t.Fatalf("Error creating session: %v", err)
	}
	session := sessionResult.Session

	defer func() {
		_, _ = ab.Delete(session)
	}()

	t.Run("command", func(t *testing.T) {
		res, err := session.Command.Run("echo 'Hello, AgentBay!'")
		if err != nil {
			t.Fatalf("Run error: %v", err)
		}
		if !res.Success {
			t.Fatalf("Run failed: %s", res.ErrorMessage)
		}
		if !strings.Contains(res.Output, "Hello, AgentBay!") {
			t.Errorf("unexpected output: %s", res.Output)
		}

		res, err = session.Command.Exec("echo 'Hello, AgentBay!'")
		if err != nil {
			t.Fatalf("Exec error: %v", err)
		}
		if !res.Success {
			t.Fatalf("Exec failed: %s", res.ErrorMessage)
		}
	})

	t.Run("filesystem", func(t *testing.T) {
		fs := session.Fs()
		writeRes, err := fs.Write("/tmp/alias_test.txt", "alias", "overwrite")
		if err != nil {
			t.Fatalf("Write error: %v", err)
		}
		if !writeRes.Success {
			t.Fatalf("Write failed")
		}

		readRes, err := fs.Read("/tmp/alias_test.txt")
		if err != nil {
			t.Fatalf("Read error: %v", err)
		}
		if !strings.Contains(readRes.Content, "alias") {
			t.Errorf("unexpected content: %s", readRes.Content)
		}

		_, err = fs.Delete("/tmp/alias_test.txt")
		if err != nil {
			t.Fatalf("Delete error: %v", err)
		}
	})

	t.Run("code", func(t *testing.T) {
		res, err := session.Code.Run("print('Hello from alias')", "python")
		if err != nil {
			t.Fatalf("Run error: %v", err)
		}
		if !strings.Contains(res.Output, "Hello from alias") {
			t.Errorf("unexpected output: %s", res.Output)
		}

		res, err = session.Code.Execute("print('Hello from alias')", "python")
		if err != nil {
			t.Fatalf("Execute error: %v", err)
		}
		if !strings.Contains(res.Output, "Hello from alias") {
			t.Errorf("unexpected output: %s", res.Output)
		}
	})
}


