package com.aliyun.agentbay.examples;

import com.aliyun.agentbay.AgentBay;
import com.aliyun.agentbay.exception.AgentBayException;
import com.aliyun.agentbay.model.BoolResult;
import com.aliyun.agentbay.model.FileInfoResult;
import com.aliyun.agentbay.model.SessionResult;
import com.aliyun.agentbay.session.CreateSessionParams;
import com.aliyun.agentbay.session.Session;

public class DeleteFileExample {

    public static void main(String[] args) {
        String apiKey = System.getenv("AGENTBAY_API_KEY");
        if (apiKey == null || apiKey.isEmpty()) {
            throw new RuntimeException("AGENTBAY_API_KEY environment variable not set");
        }

        try {
            AgentBay agentBay = new AgentBay(apiKey);
            CreateSessionParams params = new CreateSessionParams();
            params.setImageId("linux_latest");

            SessionResult sessionResult = agentBay.create(params);
            if (!sessionResult.isSuccess() || sessionResult.getSession() == null) {
                throw new RuntimeException("Failed to create session: " + sessionResult.getErrorMessage());
            }

            Session session = sessionResult.getSession();
            String remotePath = "/tmp/agentbay_delete_file_example_" + System.currentTimeMillis() + ".txt";

            try {
                BoolResult writeResult = session.getFileSystem().writeFile(remotePath, "hello delete_file");
                if (!writeResult.isSuccess()) {
                    throw new RuntimeException("write_file failed: " + writeResult.getErrorMessage());
                }

                BoolResult deleteResult = session.getFileSystem().deleteFile(remotePath);
                if (!deleteResult.isSuccess()) {
                    throw new RuntimeException("delete_file failed: " + deleteResult.getErrorMessage());
                }

                FileInfoResult infoAfter = session.getFileSystem().getFileInfo(remotePath);
                System.out.println("delete_file success: " + deleteResult.isSuccess());
                System.out.println("get_file_info after delete success: " + infoAfter.isSuccess());
            } finally {
                session.delete();
            }

        } catch (AgentBayException e) {
            System.err.println("Error: " + e.getMessage());
            e.printStackTrace();
        }
    }
}
