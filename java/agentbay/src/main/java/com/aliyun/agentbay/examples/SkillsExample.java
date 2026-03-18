package com.aliyun.agentbay.examples;

import com.aliyun.agentbay.AgentBay;
import com.aliyun.agentbay.exception.AgentBayException;
import com.aliyun.agentbay.model.CommandResult;
import com.aliyun.agentbay.model.SessionResult;
import com.aliyun.agentbay.session.CreateSessionParams;
import com.aliyun.agentbay.session.Session;
import com.aliyun.agentbay.skills.SkillMetadata;
import com.aliyun.agentbay.skills.SkillsMetadataResult;

import java.util.Arrays;
import java.util.List;

/**
 * Example demonstrating the Skills feature:
 * 1. Get skills metadata without starting a sandbox
 * 2. Get metadata filtered by group IDs
 * 3. Create session with skills loaded
 * 4. Verify skills in sandbox
 */
public class SkillsExample {

    public static void main(String[] args) {
        String apiKey = System.getenv("AGENTBAY_API_KEY");
        if (apiKey == null || apiKey.isEmpty()) {
            System.err.println("Warning: Set AGENTBAY_API_KEY environment variable.");
            return;
        }

        try {
            AgentBay agentBay = new AgentBay(apiKey);

            // 1. Get skills metadata (no sandbox needed)
            System.out.println("Getting skills metadata...");
            SkillsMetadataResult metadata = agentBay.getBetaSkills().getMetadata();
            System.out.println("Skills root path: " + metadata.getSkillsRootPath());
            System.out.println("Available skills: " + metadata.getSkills().size());
            for (SkillMetadata skill : metadata.getSkills()) {
                System.out.println("  - " + skill.getName() + ": " + skill.getDescription());
            }

            // 2. Get metadata filtered by group IDs
            System.out.println("\nGetting skills metadata filtered by group...");
            List<String> groupIds = Arrays.asList("5kvAvffm");
            SkillsMetadataResult filtered = agentBay.getBetaSkills().getMetadata(null, groupIds);
            System.out.println("Filtered skills: " + filtered.getSkills().size());

            // 3. Create session with skills loaded
            System.out.println("\nCreating session with skills...");
            CreateSessionParams params = new CreateSessionParams();
            params.setLoadSkills(true);

            SessionResult result = agentBay.create(params);
            if (!result.isSuccess() || result.getSession() == null) {
                System.err.println("Session creation failed: " + result.getErrorMessage());
                return;
            }

            Session session = result.getSession();
            try {
                System.out.println("Session created: " + session.getSessionId());
                SkillsMetadataResult sessionMeta = agentBay.getBetaSkills().getMetadata(params.getImageId(), params.getSkillNames());
                System.out.println("Session skills root: " + sessionMeta.getSkillsRootPath());
                System.out.println("Session skills count: " + sessionMeta.getSkills().size());

                // 4. Verify skills in sandbox
                if (sessionMeta.getSkillsRootPath() != null && !sessionMeta.getSkillsRootPath().isEmpty()) {
                    CommandResult cmdResult = session.getCommand().executeCommand("ls " + sessionMeta.getSkillsRootPath(), 30000);
                    if (cmdResult.isSuccess()) {
                        System.out.println("\nSkills directory contents:\n" + cmdResult.getOutput());
                    }
                }
            } finally {
                agentBay.delete(session, false);
                System.out.println("\nSession deleted.");
            }

        } catch (AgentBayException e) {
            System.err.println("Error: " + e.getMessage());
            e.printStackTrace();
        }
    }
}
