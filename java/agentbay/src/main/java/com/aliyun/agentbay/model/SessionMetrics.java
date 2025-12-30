package com.aliyun.agentbay.model;

public class SessionMetrics {
    private int cpuCount;
    private double cpuUsedPct;
    private long diskTotal;
    private long diskUsed;
    private long memTotal;
    private long memUsed;
    private double rxRateKBps;
    private double txRateKBps;
    private double rxUsedKB;
    private double txUsedKB;
    private String timestamp;

    public SessionMetrics() {
    }

    public int getCpuCount() {
        return cpuCount;
    }

    public void setCpuCount(int cpuCount) {
        this.cpuCount = cpuCount;
    }

    public double getCpuUsedPct() {
        return cpuUsedPct;
    }

    public void setCpuUsedPct(double cpuUsedPct) {
        this.cpuUsedPct = cpuUsedPct;
    }

    public long getDiskTotal() {
        return diskTotal;
    }

    public void setDiskTotal(long diskTotal) {
        this.diskTotal = diskTotal;
    }

    public long getDiskUsed() {
        return diskUsed;
    }

    public void setDiskUsed(long diskUsed) {
        this.diskUsed = diskUsed;
    }

    public long getMemTotal() {
        return memTotal;
    }

    public void setMemTotal(long memTotal) {
        this.memTotal = memTotal;
    }

    public long getMemUsed() {
        return memUsed;
    }

    public void setMemUsed(long memUsed) {
        this.memUsed = memUsed;
    }

    public double getRxRateKBps() {
        return rxRateKBps;
    }

    public void setRxRateKBps(double rxRateKBps) {
        this.rxRateKBps = rxRateKBps;
    }

    public double getTxRateKBps() {
        return txRateKBps;
    }

    public void setTxRateKBps(double txRateKBps) {
        this.txRateKBps = txRateKBps;
    }

    public double getRxUsedKB() {
        return rxUsedKB;
    }

    public void setRxUsedKB(double rxUsedKB) {
        this.rxUsedKB = rxUsedKB;
    }

    public double getTxUsedKB() {
        return txUsedKB;
    }

    public void setTxUsedKB(double txUsedKB) {
        this.txUsedKB = txUsedKB;
    }

    public String getTimestamp() {
        return timestamp;
    }

    public void setTimestamp(String timestamp) {
        this.timestamp = timestamp;
    }
}
