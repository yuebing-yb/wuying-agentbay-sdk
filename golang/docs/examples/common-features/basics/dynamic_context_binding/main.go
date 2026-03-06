package main

import (
	"fmt"
	"log"
	"os"

	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
)

func main() {
	fmt.Println("🔗 AgentBay Dynamic Context Binding Example")

	apiKey := os.Getenv("AGENTBAY_API_KEY")
	if apiKey == "" {
		log.Fatal("❌ Please set AGENTBAY_API_KEY environment variable")
	}

	agentBay, err := agentbay.NewAgentBay(apiKey)
	if err != nil {
		log.Fatalf("Failed to create AgentBay client: %v", err)
	}

	if err := dynamicBindingDemo(agentBay); err != nil {
		log.Fatalf("❌ Example execution failed: %v", err)
	}

	fmt.Println("✅ Dynamic context binding example completed")
}

func dynamicBindingDemo(agentBay *agentbay.AgentBay) error {
	fmt.Println("\n🔄 === Dynamic Context Binding Demonstration ===")

	// Step 1: Create a context
	fmt.Println("\n📦 Step 1: Creating a context...")
	contextResult, err := agentBay.Context.Get("dynamic-bind-demo", true)
	if err != nil {
		return fmt.Errorf("context creation failed: %v", err)
	}
	context := contextResult.Context
	fmt.Printf("✅ Context ready: %s (%s)\n", context.ID, context.Name)

	// Step 2: Create a session WITHOUT any initial context
	fmt.Println("\n🔧 Step 2: Creating a session (no initial context)...")
	sessionResult, err := agentBay.Create(nil)
	if err != nil {
		return fmt.Errorf("session creation failed: %v", err)
	}
	session := sessionResult.Session
	fmt.Printf("✅ Session created: %s\n", session.SessionID)

	defer func() {
		fmt.Println("\n🧹 Cleaning up...")
		agentBay.Delete(session, true)
		fmt.Println("✅ Session deleted")
	}()

	// Step 3: List bindings - should be empty
	fmt.Println("\n📋 Step 3: Listing bindings (should be empty)...")
	bindingsResult, err := session.Context.ListBindings()
	if err == nil && bindingsResult.Success {
		fmt.Printf("   Current bindings: %d\n", len(bindingsResult.Bindings))
	}

	// Step 4: Dynamically bind the context
	fmt.Println("\n🔗 Step 4: Dynamically binding context to session...")
	syncPolicy := agentbay.NewSyncPolicy()
	contextSync, _ := agentbay.NewContextSync(context.ID, "/tmp/ctx-dynamic", syncPolicy)

	bindResult, err := session.Context.Bind([]*agentbay.ContextSync{contextSync}, true)
	if err != nil {
		return fmt.Errorf("bind failed: %v", err)
	}
	if bindResult.Success {
		fmt.Printf("✅ Context bound successfully (RequestId: %s)\n", bindResult.RequestID)
	} else {
		fmt.Printf("❌ Bind failed: %s\n", bindResult.ErrorMessage)
		return nil
	}

	// Step 5: List bindings again - should show the bound context
	fmt.Println("\n📋 Step 5: Listing bindings (should show 1 binding)...")
	bindingsResult, err = session.Context.ListBindings()
	if err == nil && bindingsResult.Success {
		fmt.Printf("   Current bindings: %d\n", len(bindingsResult.Bindings))
		for _, b := range bindingsResult.Bindings {
			fmt.Printf("   - Context: %s, Path: %s, Name: %s\n", b.ContextID, b.Path, b.ContextName)
		}
	}

	// Step 6: Verify the bound context is usable
	fmt.Println("\n✍️ Step 6: Writing data to the bound context path...")
	cmdResult, err := session.Command.ExecuteCommand("echo 'Hello from dynamic binding!' > /tmp/ctx-dynamic/test.txt")
	if err == nil && cmdResult.ExitCode == 0 {
		fmt.Println("✅ Data written successfully")
	}

	readResult, err := session.FileSystem.ReadFile("/tmp/ctx-dynamic/test.txt")
	if err == nil {
		fmt.Printf("✅ Data read back: %s\n", readResult.Content)
	} else {
		fmt.Printf("❌ Failed to read data: %v\n", err)
	}

	// Step 7: Bind multiple contexts at once
	fmt.Println("\n🔗 Step 7: Demonstrating multiple context binding...")
	ctxResA, errA := agentBay.Context.Get("dynamic-bind-demo-a", true)
	ctxResB, errB := agentBay.Context.Get("dynamic-bind-demo-b", true)
	if errA == nil && errB == nil && ctxResA.Context != nil && ctxResB.Context != nil {
		csA, _ := agentbay.NewContextSync(ctxResA.Context.ID, "/tmp/ctx-multi-a", syncPolicy)
		csB, _ := agentbay.NewContextSync(ctxResB.Context.ID, "/tmp/ctx-multi-b", syncPolicy)
		bindResult2, err := session.Context.Bind([]*agentbay.ContextSync{csA, csB}, true)
		if err == nil && bindResult2.Success {
			fmt.Println("✅ Multiple contexts bound successfully")
		}

		bindingsResult, err = session.Context.ListBindings()
		if err == nil && bindingsResult.Success {
			fmt.Printf("   Total bindings: %d\n", len(bindingsResult.Bindings))
			for _, b := range bindingsResult.Bindings {
				fmt.Printf("   - %s -> %s\n", b.ContextName, b.Path)
			}
		}
	}

	return nil
}
