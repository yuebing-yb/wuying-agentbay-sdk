package com.aliyun.agentbay.examples;
import com.aliyun.agentbay.*;
import com.aliyun.agentbay.exception.AgentBayException;
import com.aliyun.agentbay.model.CodeExecutionResult;
import com.aliyun.agentbay.model.code.EnhancedCodeExecutionResult;
import com.aliyun.agentbay.session.CreateSessionParams;
import com.aliyun.agentbay.session.Session;

public class Test {
    public static void main(String[] args) throws AgentBayException {
        // Create session and execute code
        AgentBay agentBay = new AgentBay();
        CreateSessionParams params = new CreateSessionParams();
        Session session = agentBay.create(params).getSession();
        EnhancedCodeExecutionResult result = session.getCode().runCode("print('Hello AgentBay')", "python");
        if (result.isSuccess()) {
            System.out.println(result.getResult());  // Hello AgentBay
        }
        // Clean up
        agentBay.delete(session, false);
    }
}
