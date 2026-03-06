package com.aliyun.agentbay.examples;

import com.aliyun.agentbay.AgentBay;
import com.aliyun.agentbay.context.*;
import com.aliyun.agentbay.model.CommandResult;
import com.aliyun.agentbay.model.SessionResult;
import com.aliyun.agentbay.session.Session;

import com.aliyun.agentbay.session.CreateSessionParams;

import java.util.Arrays;

/**
 * Dynamic Context Binding Example
 *
 * This example demonstrates how to dynamically bind contexts to a running session:
 * 1. Create a session without any initial context
 * 2. Dynamically bind a context using session.getContext().bind()
 * 3. List current bindings using session.getContext().listBindings()
 * 4. Verify the bound context is usable
 */
public class DynamicContextBindingExample {

    public static void main(String[] args) {
        System.out.println("🔗 AgentBay Dynamic Context Binding Example");

        Session session = null;
        try {
            AgentBay agentBay = new AgentBay();

            // Step 1: Create a context
            System.out.println("\n📦 Step 1: Creating a context...");
            ContextResult contextResult = agentBay.getContext().get("dynamic-bind-demo", true);
            if (!contextResult.isSuccess() || contextResult.getContext() == null) {
                System.out.println("❌ Context creation failed");
                return;
            }
            Context context = contextResult.getContext();
            System.out.println("✅ Context ready: " + context.getId() + " (" + context.getName() + ")");

            // Step 2: Create a session WITHOUT any initial context
            System.out.println("\n🔧 Step 2: Creating a session (no initial context)...");
            SessionResult sessionResult = agentBay.create(new CreateSessionParams());
            session = sessionResult.getSession();
            System.out.println("✅ Session created: " + session.getSessionId());

            // Step 3: List bindings - should be empty
            System.out.println("\n📋 Step 3: Listing bindings (should be empty)...");
            ContextBindingsResult bindingsResult = session.getContext().listBindings();
            if (bindingsResult.isSuccess()) {
                System.out.println("   Current bindings: " + bindingsResult.getBindings().size());
            }

            // Step 4: Dynamically bind the context
            System.out.println("\n🔗 Step 4: Dynamically binding context to session...");
            SyncPolicy syncPolicy = SyncPolicy.defaultPolicy();
            ContextSync contextSync = ContextSync.create(context.getId(), "/tmp/ctx-dynamic", syncPolicy);

            ContextBindResult bindResult = session.getContext().bind(contextSync);
            if (bindResult.isSuccess()) {
                System.out.println("✅ Context bound successfully (RequestId: " + bindResult.getRequestId() + ")");
            } else {
                System.out.println("❌ Bind failed: " + bindResult.getErrorMessage());
                return;
            }

            // Step 5: List bindings again - should show the bound context
            System.out.println("\n📋 Step 5: Listing bindings (should show 1 binding)...");
            bindingsResult = session.getContext().listBindings();
            if (bindingsResult.isSuccess()) {
                System.out.println("   Current bindings: " + bindingsResult.getBindings().size());
                for (ContextBinding b : bindingsResult.getBindings()) {
                    System.out.println("   - Context: " + b.getContextId() + ", Path: " + b.getPath()
                        + ", Name: " + b.getContextName());
                }
            }

            // Step 6: Verify the bound context is usable
            System.out.println("\n✍️ Step 6: Writing data to the bound context path...");
            CommandResult cmdResult = session.getCommand().executeCommand(
                "echo 'Hello from dynamic binding!' > /tmp/ctx-dynamic/test.txt", 5000);
            if (cmdResult.isSuccess()) {
                System.out.println("✅ Data written successfully");
            }

            CommandResult readCmd = session.getCommand().executeCommand("cat /tmp/ctx-dynamic/test.txt", 5000);
            if (readCmd.isSuccess()) {
                System.out.println("✅ Data read back: " + readCmd.getOutput().trim());
            }

            // Step 7: Bind multiple contexts at once
            System.out.println("\n🔗 Step 7: Demonstrating multiple context binding...");
            ContextResult ctxResA = agentBay.getContext().get("dynamic-bind-demo-a", true);
            ContextResult ctxResB = agentBay.getContext().get("dynamic-bind-demo-b", true);
            if (ctxResA.isSuccess() && ctxResB.isSuccess()
                && ctxResA.getContext() != null && ctxResB.getContext() != null) {
                ContextSync csA = ContextSync.create(ctxResA.getContext().getId(), "/tmp/ctx-multi-a", syncPolicy);
                ContextSync csB = ContextSync.create(ctxResB.getContext().getId(), "/tmp/ctx-multi-b", syncPolicy);

                ContextBindResult bindResult2 = session.getContext().bind(
                    Arrays.asList(csA, csB), true);
                if (bindResult2.isSuccess()) {
                    System.out.println("✅ Multiple contexts bound successfully");
                }

                bindingsResult = session.getContext().listBindings();
                if (bindingsResult.isSuccess()) {
                    System.out.println("   Total bindings: " + bindingsResult.getBindings().size());
                    for (ContextBinding b : bindingsResult.getBindings()) {
                        System.out.println("   - " + b.getContextName() + " -> " + b.getPath());
                    }
                }
            }

            // Cleanup
            System.out.println("\n🧹 Cleaning up...");
            agentBay.delete(session, true);
            session = null;
            System.out.println("✅ Session deleted");

        } catch (Exception e) {
            System.err.println("❌ Error: " + e.getMessage());
            e.printStackTrace();
        }

        System.out.println("✅ Dynamic context binding example completed");
    }
}
