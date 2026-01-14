package com.aliyun.agentbay.examples;

import com.aliyun.agentbay.AgentBay;
import com.aliyun.agentbay.command.Command;
import com.aliyun.agentbay.model.CommandResult;
import com.aliyun.agentbay.model.ScreenshotBytesResult;
import com.aliyun.agentbay.session.CreateSessionParams;
import com.aliyun.agentbay.session.Session;
import com.aliyun.agentbay.model.SessionResult;
import java.nio.file.Files;
import java.nio.file.Path;

public class MobileBetaScreenshotExample {
    public static void main(String[] args) throws Exception {
        String apiKey = System.getenv("AGENTBAY_API_KEY");
        if (apiKey == null || apiKey.isEmpty()) {
            throw new IllegalArgumentException("AGENTBAY_API_KEY is not set");
        }

        AgentBay agentBay = new AgentBay();
        CreateSessionParams params = new CreateSessionParams();
        params.setImageId("imgc-0ab5takhnmlvhx9gp");

        SessionResult create = agentBay.create(params);
        if (!create.isSuccess() || create.getSession() == null) {
            throw new RuntimeException("Failed to create session: " + create.getErrorMessage());
        }

        Session session = create.getSession();
        try {
            Thread.sleep(15000);

            Command cmd = session.getCommand();
            CommandResult r1 = cmd.executeCommand("wm size 720x1280", 10000);
            if (!r1.isSuccess()) {
                throw new RuntimeException("Command failed: " + r1.getErrorMessage());
            }
            CommandResult r2 = cmd.executeCommand("wm density 160", 10000);
            if (!r2.isSuccess()) {
                throw new RuntimeException("Command failed: " + r2.getErrorMessage());
            }

            session.mobile.startApp("monkey -p com.android.settings 1");
            Thread.sleep(2000);

            Path outDir = Path.of("./tmp");
            Files.createDirectories(outDir);

            ScreenshotBytesResult s1 = session.mobile.betaTakeScreenshot();
            if (!s1.isSuccess()) {
                throw new RuntimeException("beta_take_screenshot failed: " + s1.getErrorMessage());
            }
            Path p1 = outDir.resolve("mobile_beta_screenshot.png");
            Files.write(p1, s1.getData());
            System.out.println("Saved " + p1 + " (" + s1.getData().length + " bytes)");

            ScreenshotBytesResult s2 = session.mobile.betaTakeLongScreenshot(2, "png");
            if (!s2.isSuccess()) {
                System.err.println("beta_take_long_screenshot failed: " + s2.getErrorMessage());
                return;
            }
            Path p2 = outDir.resolve("mobile_beta_long_screenshot.png");
            Files.write(p2, s2.getData());
            System.out.println("Saved " + p2 + " (" + s2.getData().length + " bytes)");
        } finally {
            agentBay.delete(session, false);
        }
    }
}

