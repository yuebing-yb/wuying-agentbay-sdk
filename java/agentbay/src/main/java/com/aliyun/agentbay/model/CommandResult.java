package com.aliyun.agentbay.model;

public class CommandResult extends ApiResponse {
    private boolean success;
    private String output;
    private String errorMessage;
    private int exitCode;
    private String stdout;
    private String stderr;
    private String traceId;

    public CommandResult() {
        this("", false, "", "", 0, "", "", "");
    }

    public CommandResult(String requestId, boolean success, String output, String errorMessage, int exitCode) {
        this(requestId, success, output, errorMessage, exitCode, "", "", "");
    }

    public CommandResult(String requestId, boolean success, String output, String errorMessage, int exitCode,
                        String stdout, String stderr, String traceId) {
        super(requestId);
        this.success = success;
        this.output = output;
        this.errorMessage = errorMessage;
        this.exitCode = exitCode;
        this.stdout = stdout;
        this.stderr = stderr;
        this.traceId = traceId;
    }

    public boolean isSuccess() {
        return success;
    }

    public void setSuccess(boolean success) {
        this.success = success;
    }

    public String getOutput() {
        return output;
    }

    public void setOutput(String output) {
        this.output = output;
    }

    public String getErrorMessage() {
        return errorMessage;
    }

    public void setErrorMessage(String errorMessage) {
        this.errorMessage = errorMessage;
    }

    public int getExitCode() {
        return exitCode;
    }

    public void setExitCode(int exitCode) {
        this.exitCode = exitCode;
    }

    public String getStdout() {
        return stdout;
    }

    public void setStdout(String stdout) {
        this.stdout = stdout;
    }

    public String getStderr() {
        return stderr;
    }

    public void setStderr(String stderr) {
        this.stderr = stderr;
    }

    public String getTraceId() {
        return traceId;
    }

    public void setTraceId(String traceId) {
        this.traceId = traceId;
    }
}