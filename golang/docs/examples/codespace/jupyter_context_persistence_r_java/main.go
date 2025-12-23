package main

import (
	"fmt"
	"os"

	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
)

// This example demonstrates that consecutive session.Code.RunCode() calls within the same
// session can share an execution context (Jupyter-like behavior) for R and Java.
func main() {
	apiKey := os.Getenv("AGENTBAY_API_KEY")
	if apiKey == "" {
		fmt.Println("Error: AGENTBAY_API_KEY environment variable not set")
		return
	}

	client, err := agentbay.NewAgentBay(apiKey)
	if err != nil {
		panic(err)
	}

	sessionResult, err := client.Create(agentbay.NewCreateSessionParams().WithImageId("code_latest"))
	if err != nil {
		panic(err)
	}
	session := sessionResult.Session
	fmt.Printf("Session created: %s\n", session.SessionID)
	defer func() {
		_, _ = client.Delete(session)
	}()

	fmt.Println("\n===== R: Jupyter-like context persistence =====")
	rSetup := `x <- 41
cat("R_CONTEXT_SETUP_DONE\n")`
	rSetupRes, err := session.Code.RunCode(rSetup, "R")
	if err != nil {
		panic(err)
	}
	fmt.Println(rSetupRes.Result)

	rUse := `cat(paste0("R_CONTEXT_VALUE:", x + 1, "\n"))`
	rUseRes, err := session.Code.RunCode(rUse, "r")
	if err != nil {
		panic(err)
	}
	fmt.Println(rUseRes.Result)

	fmt.Println("\n===== Java: Jupyter-like context persistence =====")
	javaSetup := `int x = 41;
System.out.println("JAVA_CONTEXT_SETUP_DONE");`
	javaSetupRes, err := session.Code.RunCode(javaSetup, "JAVA")
	if err != nil {
		panic(err)
	}
	fmt.Println(javaSetupRes.Result)

	javaUse := `System.out.println("JAVA_CONTEXT_VALUE:" + (x + 1));`
	javaUseRes, err := session.Code.RunCode(javaUse, "java")
	if err != nil {
		panic(err)
	}
	fmt.Println(javaUseRes.Result)
}


