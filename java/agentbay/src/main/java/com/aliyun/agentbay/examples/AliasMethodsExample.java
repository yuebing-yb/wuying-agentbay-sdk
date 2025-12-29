package com.aliyun.agentbay.examples;

import com.aliyun.agentbay.AgentBay;
import com.aliyun.agentbay.exception.AgentBayException;
import com.aliyun.agentbay.model.*;
import com.aliyun.agentbay.model.code.EnhancedCodeExecutionResult;
import com.aliyun.agentbay.session.CreateSessionParams;
import com.aliyun.agentbay.session.Session;

public class AliasMethodsExample {

    public static void main(String[] args) {
        System.out.println("=== AgentBay SDK - Alias Methods Example ===\n");
        System.out.println("This example demonstrates the ergonomic alias methods that improve");
        System.out.println("API usability and LLM-generated code success rate.\n");

        String apiKey = System.getenv("AGENTBAY_API_KEY");
        if (apiKey == null || apiKey.isEmpty()) {
            System.err.println("Error: AGENTBAY_API_KEY environment variable is not set");
            System.exit(1);
        }

        try {
            AgentBay agentBay = new AgentBay(apiKey);

            CreateSessionParams params = new CreateSessionParams();
            params.setImageId("code_latest");

            System.out.println("Creating session...");
            SessionResult result = agentBay.create(params);
            if (!result.isSuccess()) {
                System.err.println("Failed to create session: " + result.getErrorMessage());
                return;
            }

            Session session = result.getSession();
            System.out.println("Session created: " + session.getSessionId() + "\n");

            demonstrateSessionAliases(session);
            demonstrateCommandAliases(session);
            demonstrateFileSystemAliases(session);
            demonstrateCodeAliases(session);
            demonstrateRealWorldScenario(session);

            System.out.println("\nCleaning up...");
            agentBay.delete(session, false);
            System.out.println("Session deleted.\n");

            System.out.println("=== Example completed successfully ===");

        } catch (Exception e) {
            System.err.println("Error: " + e.getMessage());
            e.printStackTrace();
        }
    }

    private static void demonstrateSessionAliases(Session session) {
        System.out.println("📁 Session FileSystem Aliases");
        System.out.println("─────────────────────────────");
        System.out.println("The Session class provides convenient aliases for accessing the FileSystem:");
        System.out.println("  • session.fs()           - Short and intuitive");
        System.out.println("  • session.getFilesystem() - Alternative naming");
        System.out.println("  • session.getFiles()      - Another alternative");
        System.out.println();

        System.out.println("All three return the same FileSystem instance:");
        System.out.println("  session.getFileSystem() == session.fs() : " +
            (session.getFileSystem() == session.fs()));
        System.out.println("  session.getFileSystem() == session.getFilesystem() : " +
            (session.getFileSystem() == session.getFilesystem()));
        System.out.println("  session.getFileSystem() == session.getFiles() : " +
            (session.getFileSystem() == session.getFiles()));
        System.out.println();
    }

    private static void demonstrateCommandAliases(Session session) {
        System.out.println("⚡ Command Execution Aliases");
        System.out.println("────────────────────────────");
        System.out.println("The Command class provides intuitive aliases:");
        System.out.println("  • command.run(cmd)  - Alias of executeCommand()");
        System.out.println("  • command.exec(cmd) - Another alias of executeCommand()");
        System.out.println();

        try {
            System.out.println("Using run() alias:");
            CommandResult result1 = session.getCommand().run("echo 'Hello from run()'", 5000);
            System.out.println("  Output: " + result1.getOutput().trim());

            System.out.println("\nUsing exec() alias:");
            CommandResult result2 = session.getCommand().exec("echo 'Hello from exec()'", 5000);
            System.out.println("  Output: " + result2.getOutput().trim());

            System.out.println("\nOriginal executeCommand() still works:");
            CommandResult result3 = session.getCommand().executeCommand("echo 'Hello from executeCommand()'", 5000);
            System.out.println("  Output: " + result3.getOutput().trim());
            System.out.println();

        } catch (Exception e) {
            System.err.println("Error: " + e.getMessage());
        }
    }

    private static void demonstrateFileSystemAliases(Session session) throws AgentBayException {
        System.out.println("📂 FileSystem Operation Aliases");
        System.out.println("───────────────────────────────");
        System.out.println("The FileSystem class provides familiar Unix-like aliases:");
        System.out.println("  • fs.ls(path)     - Alias of listDirectory()");
        System.out.println("  • fs.rm(path)     - Alias of deleteFile()");
        System.out.println("  • fs.delete(path) - Another alias of deleteFile()");
        System.out.println();

        String testDir = "/tmp/alias_demo";
        session.fs().createDirectory(testDir);
        System.out.println("Created test directory: " + testDir);

        session.fs().writeFile(testDir + "/file1.txt", "Content 1");
        session.fs().writeFile(testDir + "/file2.txt", "Content 2");
        session.fs().writeFile(testDir + "/file3.txt", "Content 3");
        System.out.println("Created 3 test files");

        System.out.println("\nUsing ls() alias to list directory:");
        DirectoryListResult lsResult = session.fs().ls(testDir);
        System.out.println("  Found " + lsResult.getEntries().size() + " entries");

        System.out.println("\nUsing rm() alias to remove files:");
        session.fs().rm(testDir + "/file1.txt");
        System.out.println("  Removed file1.txt with rm()");

        System.out.println("\nUsing delete() alias to remove files:");
        session.fs().delete(testDir + "/file2.txt");
        System.out.println("  Removed file2.txt with delete()");

        System.out.println("\nVerifying with ls() again:");
        DirectoryListResult lsResult2 = session.fs().ls(testDir);
        System.out.println("  Now " + lsResult2.getEntries().size() + " entries remaining");

        session.fs().rm(testDir + "/file3.txt");
        System.out.println();
    }

    private static void demonstrateCodeAliases(Session session) {
        System.out.println("🐍 Code Execution Aliases");
        System.out.println("─────────────────────────");
        System.out.println("The Code class provides intuitive aliases:");
        System.out.println("  • code.run(code, lang)         - Alias of runCode()");
        System.out.println("  • code.run(code, lang, timeout) - With timeout parameter");
        System.out.println();

        try {
            System.out.println("Using run() alias for Python:");
            String pythonCode = "result = 2 + 2\nprint(f'2 + 2 = {result}')";
            EnhancedCodeExecutionResult result1 = session.getCode().run(pythonCode, "python");
            System.out.println("  Success: " + result1.isSuccess());
            if (result1.getResults() != null && !result1.getResults().isEmpty()) {
                System.out.println("  Output: " + result1.getResults().get(0).getText());
            }

            System.out.println("\nUsing run() with timeout:");
            String jsCode = "const x = 10;\nconst y = 20;\nconsole.log(`${x} + ${y} = ${x + y}`);";
            EnhancedCodeExecutionResult result2 = session.getCode().run(jsCode, "javascript", 10);
            System.out.println("  Success: " + result2.isSuccess());

            System.out.println("\nOriginal runCode() still works:");
            EnhancedCodeExecutionResult result3 = session.getCode().runCode("print('Hello')", "python");
            System.out.println("  Success: " + result3.isSuccess());
            System.out.println();

        } catch (Exception e) {
            System.err.println("Error: " + e.getMessage());
        }
    }

    private static void demonstrateRealWorldScenario(Session session) throws AgentBayException {
        System.out.println("🌍 Real-World Scenario: Data Processing Pipeline");
        System.out.println("─────────────────────────────────────────────────");
        System.out.println("This scenario demonstrates how aliases make code more readable and intuitive.\n");

        String projectDir = "/tmp/data_pipeline";

        System.out.println("Step 1: Set up project structure using fs() alias");
        session.fs().createDirectory(projectDir);
        session.fs().createDirectory(projectDir + "/input");
        session.fs().createDirectory(projectDir + "/output");

        System.out.println("Step 2: Create sample data files");
        session.fs().writeFile(projectDir + "/input/data1.csv", "id,value\n1,100\n2,200\n3,300");
        session.fs().writeFile(projectDir + "/input/data2.csv", "id,value\n4,400\n5,500\n6,600");

        System.out.println("Step 3: List input files using ls() alias");
        DirectoryListResult inputFiles = session.fs().ls(projectDir + "/input");
        System.out.println("  Found " + inputFiles.getEntries().size() + " input files");

        System.out.println("\nStep 4: Process data using Python code.run() alias");
        String processingCode = String.format(
            "import os\n" +
            "input_dir = '%s/input'\n" +
            "output_dir = '%s/output'\n" +
            "files = os.listdir(input_dir)\n" +
            "print(f'Processing {len(files)} files...')\n" +
            "for file in files:\n" +
            "    with open(os.path.join(input_dir, file), 'r') as f:\n" +
            "        lines = f.readlines()\n" +
            "        print(f'  {file}: {len(lines)-1} records')\n" +
            "print('Processing complete!')",
            projectDir, projectDir
        );
        EnhancedCodeExecutionResult processResult = session.getCode().run(processingCode, "python");
        System.out.println("  " + (processResult.isSuccess() ? "Success" : "Failed"));

        System.out.println("\nStep 5: Verify results using command.run() alias");
        CommandResult verifyResult = session.getCommand().run(
            "find " + projectDir + " -type f | wc -l", 5000);
        System.out.println("  Total files: " + verifyResult.getOutput().trim());

        System.out.println("\nStep 6: Clean up using rm() alias");
        session.fs().rm(projectDir + "/input/data1.csv");
        session.fs().rm(projectDir + "/input/data2.csv");
        System.out.println("  Cleaned up data files");

        System.out.println("\n✅ Pipeline completed successfully!");
        System.out.println("\nKey takeaways:");
        System.out.println("  • fs() is shorter than getFileSystem()");
        System.out.println("  • ls() is more intuitive than listDirectory()");
        System.out.println("  • rm() matches Unix convention");
        System.out.println("  • run() is concise for both commands and code");
        System.out.println("  • Aliases make code more readable and LLM-friendly");
        System.out.println();
    }
}
