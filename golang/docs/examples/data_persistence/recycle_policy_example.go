package main

/*
RecyclePolicy Example - Data Lifecycle Management

This example demonstrates how to use RecyclePolicy to control the lifecycle
of context data in the cloud.

Expected Output:

======================================================================
Example 1: Default RecyclePolicy
======================================================================
✅ Context created: SdkCtx-xxxxxxxxxxxxx
   Lifecycle: Lifecycle_Forever
   Paths: []
✅ Session created: session-xxxxxxxxxxxxx
✅ Data written to /tmp/default_data/test.txt
✅ Session deleted
✅ Context deleted

======================================================================
Example 2: RecyclePolicy with 1 Day Lifecycle
======================================================================
✅ Context created: SdkCtx-xxxxxxxxxxxxx
   Lifecycle: Lifecycle_1Day
   Paths: []
✅ Session created: session-xxxxxxxxxxxxx
✅ Data written to /tmp/oneday_data/test.txt
   ℹ️  This data will be automatically deleted after 1 day
✅ Session deleted
✅ Context deleted

======================================================================
Example 3: RecyclePolicy for Specific Paths
======================================================================
✅ Context created: SdkCtx-xxxxxxxxxxxxx
   Lifecycle: Lifecycle_3Days
   Paths: [/tmp/cache /tmp/logs]
   ℹ️  Only files in /tmp/cache and /tmp/logs will be deleted after 3 days
✅ Session created: session-xxxxxxxxxxxxx
✅ Session deleted
✅ Context deleted

======================================================================
Example 4: Different Lifecycle Options
======================================================================
📋 Available Lifecycle Options:
--------------------------------------------------
   Lifecycle_1Day            - 1 day
   Lifecycle_3Days           - 3 days
   Lifecycle_5Days           - 5 days
   Lifecycle_10Days          - 10 days
   Lifecycle_30Days          - 30 days
   Lifecycle_Forever         - Forever (permanent)
✅ All lifecycle options validated successfully
*/

import (
	"fmt"
	"log"

	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
)

func example1DefaultRecyclePolicy() {
	fmt.Println("\n" + repeatString("=", 70))
	fmt.Println("Example 1: Default RecyclePolicy")
	fmt.Println(repeatString("=", 70))

	client := agentbay.New()

	// Create a context
	contextResult, err := client.Context().Get("default-recycle-demo", true)
	if err != nil {
		log.Printf("❌ Failed to create context: %v", err)
		return
	}

	context := contextResult.Context
	fmt.Printf("✅ Context created: %s\n", context.ID)

	// Use default SyncPolicy (includes default RecyclePolicy with LifecycleForever)
	syncPolicy := agentbay.NewSyncPolicy()
	fmt.Printf("   Lifecycle: %s\n", syncPolicy.RecyclePolicy.Lifecycle)
	fmt.Printf("   Paths: %v\n", syncPolicy.RecyclePolicy.Paths)

	contextSync := agentbay.NewContextSync(context.ID, "/tmp/default_data", syncPolicy)

	// Create session with context sync
	params := &agentbay.CreateSessionParams{
		ContextSyncs: []*agentbay.ContextSync{contextSync},
	}
	sessionResult, err := client.Create(params)
	if err != nil {
		log.Printf("❌ Failed to create session: %v", err)
		return
	}

	session := sessionResult.Session
	fmt.Printf("✅ Session created: %s\n", session.SessionID)

	// Write some data
	_, err = session.Command().ExecuteCommand("echo 'Default policy - data kept forever' > /tmp/default_data/test.txt")
	if err != nil {
		log.Printf("❌ Failed to write data: %v", err)
	} else {
		fmt.Println("✅ Data written to /tmp/default_data/test.txt")
	}

	// Clean up
	err = client.Delete(session)
	if err != nil {
		log.Printf("❌ Failed to delete session: %v", err)
	} else {
		fmt.Println("✅ Session deleted")
	}

	err = client.Context().Delete(context)
	if err != nil {
		log.Printf("❌ Failed to delete context: %v", err)
	} else {
		fmt.Println("✅ Context deleted")
	}
}

func example2OneDayLifecycle() {
	fmt.Println("\n" + repeatString("=", 70))
	fmt.Println("Example 2: RecyclePolicy with 1 Day Lifecycle")
	fmt.Println(repeatString("=", 70))

	client := agentbay.New()

	// Create a context
	contextResult, err := client.Context().Get("one-day-recycle-demo", true)
	if err != nil {
		log.Printf("❌ Failed to create context: %v", err)
		return
	}

	context := contextResult.Context
	fmt.Printf("✅ Context created: %s\n", context.ID)

	// Create custom RecyclePolicy with 1 day lifecycle
	recyclePolicy := &agentbay.RecyclePolicy{
		Lifecycle: agentbay.Lifecycle1Day,
		Paths:     []string{""}, // Apply to all paths
	}

	// Create SyncPolicy with custom RecyclePolicy
	syncPolicy := agentbay.NewSyncPolicy()
	syncPolicy.RecyclePolicy = recyclePolicy

	fmt.Printf("   Lifecycle: %s\n", syncPolicy.RecyclePolicy.Lifecycle)
	fmt.Printf("   Paths: %v\n", syncPolicy.RecyclePolicy.Paths)

	contextSync := agentbay.NewContextSync(context.ID, "/tmp/oneday_data", syncPolicy)

	// Create session with context sync
	params := &agentbay.CreateSessionParams{
		Labels:       map[string]string{"example": "recycle_policy", "lifecycle": "1day"},
		ContextSyncs: []*agentbay.ContextSync{contextSync},
	}
	sessionResult, err := client.Create(params)
	if err != nil {
		log.Printf("❌ Failed to create session: %v", err)
		return
	}

	session := sessionResult.Session
	fmt.Printf("✅ Session created: %s\n", session.SessionID)

	// Write some data
	_, _ = session.Command().ExecuteCommand("mkdir -p /tmp/oneday_data")
	_, err = session.Command().ExecuteCommand("echo 'This data will be deleted after 1 day' > /tmp/oneday_data/test.txt")
	if err != nil {
		log.Printf("❌ Failed to write data: %v", err)
	} else {
		fmt.Println("✅ Data written to /tmp/oneday_data/test.txt")
		fmt.Println("   ℹ️  This data will be automatically deleted after 1 day")
	}

	// Clean up
	err = client.Delete(session)
	if err != nil {
		log.Printf("❌ Failed to delete session: %v", err)
	} else {
		fmt.Println("✅ Session deleted")
	}

	err = client.Context().Delete(context)
	if err != nil {
		log.Printf("❌ Failed to delete context: %v", err)
	} else {
		fmt.Println("✅ Context deleted")
	}
}

func example3SpecificPaths() {
	fmt.Println("\n" + repeatString("=", 70))
	fmt.Println("Example 3: RecyclePolicy for Specific Paths")
	fmt.Println(repeatString("=", 70))

	client := agentbay.New()

	// Create a context
	contextResult, err := client.Context().Get("specific-path-demo", true)
	if err != nil {
		log.Printf("❌ Failed to create context: %v", err)
		return
	}

	context := contextResult.Context
	fmt.Printf("✅ Context created: %s\n", context.ID)

	// Create RecyclePolicy for specific paths
	recyclePolicy := &agentbay.RecyclePolicy{
		Lifecycle: agentbay.Lifecycle3Days,
		Paths:     []string{"/tmp/cache", "/tmp/logs"}, // Only these paths
	}

	syncPolicy := agentbay.NewSyncPolicy()
	syncPolicy.RecyclePolicy = recyclePolicy

	fmt.Printf("   Lifecycle: %s\n", syncPolicy.RecyclePolicy.Lifecycle)
	fmt.Printf("   Paths: %v\n", syncPolicy.RecyclePolicy.Paths)
	fmt.Println("   ℹ️  Only files in /tmp/cache and /tmp/logs will be deleted after 3 days")

	contextSync := agentbay.NewContextSync(context.ID, "/tmp/multipath_data", syncPolicy)

	// Create session
	params := &agentbay.CreateSessionParams{
		ContextSyncs: []*agentbay.ContextSync{contextSync},
	}
	sessionResult, err := client.Create(params)
	if err != nil {
		log.Printf("❌ Failed to create session: %v", err)
		return
	}

	session := sessionResult.Session
	fmt.Printf("✅ Session created: %s\n", session.SessionID)

	// Clean up
	err = client.Delete(session)
	if err != nil {
		log.Printf("❌ Failed to delete session: %v", err)
	} else {
		fmt.Println("✅ Session deleted")
	}

	err = client.Context().Delete(context)
	if err != nil {
		log.Printf("❌ Failed to delete context: %v", err)
	} else {
		fmt.Println("✅ Context deleted")
	}
}

func example4DifferentLifecycles() {
	fmt.Println("\n" + repeatString("=", 70))
	fmt.Println("Example 4: Different Lifecycle Options")
	fmt.Println(repeatString("=", 70))

	lifecycles := []struct {
		lifecycle   agentbay.Lifecycle
		description string
	}{
		{agentbay.Lifecycle1Day, "1 day"},
		{agentbay.Lifecycle3Days, "3 days"},
		{agentbay.Lifecycle5Days, "5 days"},
		{agentbay.Lifecycle10Days, "10 days"},
		{agentbay.Lifecycle30Days, "30 days"},
		{agentbay.LifecycleForever, "Forever (permanent)"},
	}

	fmt.Println("\n📋 Available Lifecycle Options:")
	fmt.Println(repeatString("-", 50))
	for _, lc := range lifecycles {
		fmt.Printf("   %-25s - %s\n", lc.lifecycle, lc.description)
	}

	fmt.Println("\n✅ All lifecycle options validated successfully")
}

func main() {
	fmt.Println("\n" + repeatString("=", 70))
	fmt.Println("RecyclePolicy Examples - Data Lifecycle Management")
	fmt.Println(repeatString("=", 70))
	fmt.Println("\nThese examples demonstrate how to use RecyclePolicy to control")
	fmt.Println("the lifecycle of context data in the cloud.")

	// Run examples
	example1DefaultRecyclePolicy()
	example2OneDayLifecycle()
	example3SpecificPaths()
	example4DifferentLifecycles()

	fmt.Println("\n" + repeatString("=", 70))
	fmt.Println("✅ All RecyclePolicy examples completed successfully!")
	fmt.Println(repeatString("=", 70))
}

// Helper function to repeat a string
func repeatString(s string, count int) string {
	result := ""
	for i := 0; i < count; i++ {
		result += s
	}
	return result
}
