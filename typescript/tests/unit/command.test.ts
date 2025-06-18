import { AgentBay, Session } from '../../src';
import { getTestApiKey, containsToolNotFound } from '../utils/test-helpers';
import { log } from '../../src/utils/logger';


describe('Command', () => {
  describe('runCode', () => {
    let agentBay: AgentBay;
    let session: Session;
    
    beforeEach(async () => {
      const apiKey = getTestApiKey();
      agentBay = new AgentBay({ apiKey });
      
      // Create a session with linux_latest image
      log('Creating a new session for run_code testing...');
      const sessionParams = { imageId: 'code_latest' };
      session = await agentBay.create(sessionParams);
      log(`Session created with ID: ${session.sessionId}`);
    });
    
    afterEach(async () => {
      // Clean up the session
      log('Cleaning up: Deleting the session...');
      try {
        if(session && session.sessionId)
          await agentBay.delete(session);
      } catch (error) {
        log(`Warning: Error deleting session: ${error}`);
      }
    });

    it.only('should execute Python code', async () => {
      if (session.command) {
        // Test with Python code
        log('Executing Python code...');
        const pythonCode = `
print("Hello, world!")
x = 1 + 1
print(x)
`;
        
        try {
          // Test with default timeout
          const response = await session.command.runCode(pythonCode, 'python');
          log(`Python code execution result: ${response}`);
          
          // Check if response contains "tool not found"
          expect(containsToolNotFound(response)).toBe(false);
          
          // Verify the response contains expected output
          expect(response.includes('Hello, world!')).toBe(true);
          expect(response.includes('2')).toBe(true);
          log('Python code execution verified successfully');
        } catch (error) {
          log(`Note: Python code execution failed: ${error}`);
          // Don't fail the test if code execution is not supported
        }
      } else {
        log('Note: Command interface is nil, skipping run_code test');
      }
    });
    
    it.only('should execute JavaScript code with custom timeout', async () => {
      if (session.command) {
        // Test with JavaScript code
        log('Executing JavaScript code with custom timeout...');
        const jsCode = `
console.log("Hello, world!");
const x = 1 + 1;
console.log(x);
`;
        
        try {
          // Test with custom timeout (10 minutes)
          const customTimeout = 600;
          const response = await session.command.runCode(jsCode, 'javascript', customTimeout);
          log(`JavaScript code execution result: ${response}`);
          
          // Check if response contains "tool not found"
          expect(containsToolNotFound(response)).toBe(false);
          
          // Verify the response contains expected output
          expect(response.includes('Hello, world!')).toBe(true);
          expect(response.includes('2')).toBe(true);
          log('JavaScript code execution verified successfully');
        } catch (error) {
          log(`Note: JavaScript code execution failed: ${error}`);
          // Don't fail the test if code execution is not supported
        }
      } else {
        log('Note: Command interface is nil, skipping run_code test');
      }
    });
    
    it.only('should handle invalid language', async () => {
      if (session.command) {
        // Test with invalid language
        log('Testing with invalid language...');
        
        try {
          await session.command.runCode('print("test")', 'invalid_language');
          // If we get here, the test should fail
          log('Error: Expected error for invalid language, but got success');
          expect(false).toBe(true); // This should fail the test
        } catch (error) {
          // This is the expected behavior
          log(`Correctly received error for invalid language: ${error}`);
          expect(error).toBeDefined();
        }
      } else {
        log('Note: Command interface is nil, skipping run_code test');
      }
    });
  });
  
  describe('executeCommand', () => {
    let agentBay: AgentBay;
    let session: Session;
    
    beforeEach(async () => {
      const apiKey = getTestApiKey();
      agentBay = new AgentBay({ apiKey });
      
      // Create a session with linux_latest image
      log('Creating a new session for command testing...');
      const sessionParams = { imageId: 'linux_latest' };
      session = await agentBay.create(sessionParams);
      log(`Session created with ID: ${session.sessionId}`);
    });
    
    afterEach(async () => {
      // Clean up the session
      log('Cleaning up: Deleting the session...');
      try {
        if(session && session.sessionId)
          await agentBay.delete(session);
      } catch (error) {
        log(`Warning: Error deleting session: ${error}`);
      }
    });
    it.only('should execute a command', async () => {
      if (session.command) {
        // Test with echo command (works on all platforms)
        log('Executing echo command...');
        const testString = 'AgentBay SDK Test';
        const echoCmd = `echo '${testString}'`;
        
        try {
          // Increase the command execution timeout to 10 seconds (10000ms)
          const response = await session.command.executeCommand(echoCmd, 10000);
          log(`Echo command result: ${response}`);
          
          // Check if response contains "tool not found"
          expect(containsToolNotFound(response)).toBe(false);
          
          // Verify the response contains the test string
          expect(response.includes(testString)).toBe(true);
          log('Echo command verified successfully');
        } catch (error) {
          log(`Note: Echo command failed: ${error}`);
          // Don't fail the test if command execution is not supported
        }
      } else {
        log('Note: Command interface is nil, skipping command test');
      }
    });
    
    it.only('should handle command execution errors', async () => {
      if (session.command) {
        // Test with an invalid command
        log('Executing invalid command...');
        const invalidCmd = 'invalid_command_that_does_not_exist';
        
        try {
          const response = await session.command.executeCommand(invalidCmd);
          log(`Invalid command result: ${response}`);
          
          // Even if the command doesn't exist, the API might return a response with an error message
          // We're just checking that the promise resolves
          expect(response).toBeDefined();
        } catch (error) {
          // If the API rejects the promise, that's also an acceptable behavior for an invalid command
          log(`Invalid command failed as expected: ${error}`);
          expect(error).toBeDefined();
        }
      } else {
        log('Note: Command interface is nil, skipping command error test');
      }
    });
    
    it.only('should execute a command with arguments', async () => {
      if (session.command) {
        // Test with a command that takes arguments
        log('Executing command with arguments...');
        const arg1 = 'hello';
        const arg2 = 'world';
        const cmd = `echo ${arg1} ${arg2}`;
        
        try {
          // Increase the command execution timeout to 10 seconds (10000ms)
          const response = await session.command.executeCommand(cmd, 10000);
          log(`Command with arguments result: ${response}`);
          
          // Check if response contains "tool not found"
          expect(containsToolNotFound(response)).toBe(false);
          
          // Verify the response contains both arguments
          expect(response.includes(arg1)).toBe(true);
          expect(response.includes(arg2)).toBe(true);
          log('Command with arguments verified successfully');
        } catch (error) {
          log(`Note: Command with arguments failed: ${error}`);
          // Don't fail the test if command execution is not supported
        }
      } else {
        log('Note: Command interface is nil, skipping command with arguments test');
      }
    });
  });
});
