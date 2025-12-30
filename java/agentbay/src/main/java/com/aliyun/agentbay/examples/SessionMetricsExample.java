package com.aliyun.agentbay.examples;

import com.aliyun.agentbay.AgentBay;
import com.aliyun.agentbay.exception.AgentBayException;
import com.aliyun.agentbay.model.SessionMetrics;
import com.aliyun.agentbay.model.SessionMetricsResult;
import com.aliyun.agentbay.model.SessionResult;
import com.aliyun.agentbay.session.CreateSessionParams;

public class SessionMetricsExample {
    public static void main(String[] args) {
        try {
            AgentBay agentBay = new AgentBay();

            System.out.println("Creating session with linux_latest image...");
            CreateSessionParams params = new CreateSessionParams();
            params.setImageId("code_latest");

            SessionResult createResult = agentBay.create(params);
            if (!createResult.isSuccess() || createResult.getSession() == null) {
                System.err.println("Failed to create session: " + createResult.getErrorMessage());
                return;
            }

            System.out.println("Session created: " + createResult.getSession().getSessionId());

            System.out.println("\nRetrieving session metrics...");
            SessionMetricsResult metricsResult = createResult.getSession().getMetrics();

            if (!metricsResult.isSuccess()) {
                System.err.println("Failed to get metrics: " + metricsResult.getErrorMessage());
                createResult.getSession().delete();
                return;
            }

            SessionMetrics metrics = metricsResult.getMetrics();
            if (metrics == null) {
                System.err.println("No metrics data returned");
                createResult.getSession().delete();
                return;
            }

            System.out.println("\n=== Session Metrics ===");
            System.out.println("Timestamp: " + metrics.getTimestamp());
            System.out.println("\nCPU:");
            System.out.println("  CPU Count: " + metrics.getCpuCount());
            System.out.println("  CPU Used: " + String.format("%.2f%%", metrics.getCpuUsedPct()));
            System.out.println("\nMemory:");
            System.out.println("  Total: " + formatBytes(metrics.getMemTotal()));
            System.out.println("  Used: " + formatBytes(metrics.getMemUsed()));
            System.out.println("  Usage: " + String.format("%.2f%%",
                (double) metrics.getMemUsed() / metrics.getMemTotal() * 100));
            System.out.println("\nDisk:");
            System.out.println("  Total: " + formatBytes(metrics.getDiskTotal()));
            System.out.println("  Used: " + formatBytes(metrics.getDiskUsed()));
            System.out.println("  Usage: " + String.format("%.2f%%",
                (double) metrics.getDiskUsed() / metrics.getDiskTotal() * 100));
            System.out.println("\nNetwork:");
            System.out.println("  RX Rate: " + String.format("%.2f KB/s", metrics.getRxRateKBps()));
            System.out.println("  TX Rate: " + String.format("%.2f KB/s", metrics.getTxRateKBps()));
            System.out.println("  RX Total: " + String.format("%.2f KB", metrics.getRxUsedKB()));
            System.out.println("  TX Total: " + String.format("%.2f KB", metrics.getTxUsedKB()));

            System.out.println("\n=== Raw Metrics Data ===");
            if (metricsResult.getRaw() != null) {
                metricsResult.getRaw().forEach((key, value) ->
                    System.out.println("  " + key + ": " + value));
            }

            System.out.println("\nDeleting session...");
            createResult.getSession().delete();
            System.out.println("Session deleted successfully");

        } catch (AgentBayException e) {
            System.err.println("Error: " + e.getMessage());
            e.printStackTrace();
        }
    }

    private static String formatBytes(long bytes) {
        if (bytes < 1024) {
            return bytes + " B";
        } else if (bytes < 1024 * 1024) {
            return String.format("%.2f KB", bytes / 1024.0);
        } else if (bytes < 1024 * 1024 * 1024) {
            return String.format("%.2f MB", bytes / (1024.0 * 1024));
        } else {
            return String.format("%.2f GB", bytes / (1024.0 * 1024 * 1024));
        }
    }
}

