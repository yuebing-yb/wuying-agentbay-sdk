package com.aliyun.agentbay;

import com.aliyun.agentbay.browser.BrowserContext;
import com.aliyun.agentbay.client.ApiClient;
import com.aliyun.agentbay.context.*;
import com.aliyun.agentbay.exception.AgentBayException;
import com.aliyun.agentbay.exception.AuthenticationException;
import com.aliyun.agentbay.mobile.MobileSimulate;
import com.aliyun.agentbay.mobile.MobileSimulateConfig;
import com.aliyun.agentbay.mobile.MobileSimulateMode;
import com.aliyun.agentbay.model.GetSessionData;
import com.aliyun.agentbay.model.GetSessionResult;
import com.aliyun.agentbay.model.SessionParams;
import com.aliyun.agentbay.model.SessionResult;
import com.aliyun.agentbay.network.Network;
import com.aliyun.agentbay.session.Session;
import com.aliyun.agentbay.session.CreateSessionParams;
import com.aliyun.agentbay.util.ResponseUtil;
import com.aliyun.agentbay.util.Version;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.aliyun.teaopenapi.models.Config;
import com.aliyun.wuyingai20250506.Client;
import com.aliyun.wuyingai20250506.models.CreateMcpSessionRequest;
import com.aliyun.wuyingai20250506.models.CreateMcpSessionResponse;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

/**
 * Main client for interacting with the AgentBay cloud runtime environment
 */
public class AgentBay {
    private static final ObjectMapper objectMapper = new ObjectMapper();

    private String apiKey;
    private String regionId;
    private Client client;
    private ApiClient apiClient;
    private ConcurrentHashMap<String, Session> sessions;
    private MobileSimulate mobileSimulate;
    private Network network;

    public AgentBay() throws AgentBayException {
        this(null, null);
    }

    public AgentBay(String apiKey) throws AgentBayException {
        this(apiKey, null);
    }

    public AgentBay(String apiKey, com.aliyun.agentbay.Config config) throws AgentBayException {
        if (config == null) {
            config = new com.aliyun.agentbay.Config();
        }

        if (apiKey == null || apiKey.trim().isEmpty()) {
            apiKey = System.getenv("AGENTBAY_API_KEY");
            if (apiKey == null || apiKey.trim().isEmpty()) {
                throw new AuthenticationException(
                    "API key is required. Provide it as a parameter or set the " +
                    "AGENTBAY_API_KEY environment variable"
                );
            }
        }

        this.apiKey = apiKey;
        this.regionId = config.getRegionId();
        this.sessions = new ConcurrentHashMap<>();

        try {
            // Initialize the OpenAPI client
            Config clientConfig = new Config();
            clientConfig.setEndpoint(config.getEndpoint());
            clientConfig.setAccessKeyId("Bearer");
            clientConfig.setAccessKeySecret(apiKey);
            clientConfig.setReadTimeout(config.getTimeoutMs());
            clientConfig.setConnectTimeout(config.getTimeoutMs());

            this.client = new Client(clientConfig);
            this.apiClient = new ApiClient(this.client, apiKey);
            this.mobileSimulate = new MobileSimulate(this);
            this.network = new Network(this);
        } catch (Exception e) {
            throw new AgentBayException("Failed to initialize AgentBay client", e);
        }
    }

    /**
     * Get an existing session by ID from local cache only.
     * This method only retrieves sessions from the local cache (sessions created by this AgentBay instance).
     * It does not fetch sessions from the server.
     *
     * @param sessionId The session ID
     * @return Session object if found in cache, null otherwise
     */
    public Session getSession(String sessionId) {
        return sessions.get(sessionId);
    }

    /**
     * Get session information by session ID from remote server.
     * This method retrieves detailed session metadata from the API without creating a Session object.
     *
     * @param sessionId The ID of the session to retrieve
     * @return GetSessionResult containing session information
     */
    public GetSessionResult getSessionInfo(String sessionId) {
        try {
            com.aliyun.wuyingai20250506.models.GetSessionRequest request = 
                new com.aliyun.wuyingai20250506.models.GetSessionRequest();
            request.setAuthorization("Bearer " + apiKey);
            request.setSessionId(sessionId);

            com.aliyun.wuyingai20250506.models.GetSessionResponse response = client.getSession(request);

            String requestId = ResponseUtil.extractRequestId(response);

            if (response == null || response.getBody() == null) {
                return new GetSessionResult(
                    requestId,
                    false,
                    null,
                    "Invalid response from GetSession API"
                );
            }

            com.aliyun.wuyingai20250506.models.GetSessionResponseBody body = response.getBody();
            Boolean success = body.getSuccess();
            String code = body.getCode();
            String message = body.getMessage();

            // Check for API-level errors
            if (success == null || !success) {
                String errorMsg = message != null ? message : "Unknown error";
                if (code != null) {
                    errorMsg = "[" + code + "] " + errorMsg;
                }
                return new GetSessionResult(
                    requestId,
                    false,
                    null,
                    errorMsg
                );
            }

            // Extract session data
            GetSessionData data = null;
            if (body.getData() != null) {
                com.aliyun.wuyingai20250506.models.GetSessionResponseBody.GetSessionResponseBodyData responseData = 
                    body.getData();
                data = new GetSessionData(
                    responseData.getSessionId(),
                    responseData.getAppInstanceId(),
                    responseData.getResourceId(),
                    responseData.getResourceUrl(),
                    responseData.getVpcResource() != null ? responseData.getVpcResource() : false,
                    responseData.getNetworkInterfaceIp(),
                    responseData.getHttpPort(),
                    responseData.getToken(),
                    body.getCode() != null ? body.getCode() : ""
                );
            }

            return new GetSessionResult(
                requestId,
                true,
                data,
                ""
            );

        } catch (com.aliyun.tea.TeaException e) {
            String errorStr = e.getMessage();
            String requestId = "";
            if (e.getData() != null && e.getData().get("RequestId") != null) {
                requestId = e.getData().get("RequestId").toString();
            }

            // Check if this is an expected business error (e.g., session not found)
            if (errorStr != null && (errorStr.contains("InvalidMcpSession.NotFound") || 
                                     errorStr.contains("NotFound"))) {
                return new GetSessionResult(
                    requestId,
                    false,
                    null,
                    "Session " + sessionId + " not found"
                );
            } else {
                return new GetSessionResult(
                    requestId,
                    false,
                    null,
                    "Failed to get session " + sessionId + ": " + errorStr
                );
            }
        } catch (Exception e) {
            return new GetSessionResult(
                "",
                false,
                null,
                "Failed to get session " + sessionId + ": " + e.getMessage()
            );
        }
    }

    /**
     * Get a session by its ID from remote server.
     * This method calls the GetSession API to retrieve session information and creates a Session object.
     * Unlike getSession(), this method fetches from the remote server, enabling session recovery scenarios.
     *
     * @param sessionId The ID of the session to retrieve. Must be a non-empty string.
     * @return SessionResult containing the Session instance, request ID, and success status.
     * @throws AgentBayException if the API request fails
     */
    public SessionResult get(String sessionId) throws AgentBayException {
        // Validate input
        if (sessionId == null || sessionId.trim().isEmpty()) {
            SessionResult result = new SessionResult();
            result.setSuccess(false);
            result.setErrorMessage("session_id is required");
            result.setRequestId("");
            return result;
        }

        // Call GetSession API
        GetSessionResult getResult = getSessionInfo(sessionId);

        // Check if the API call was successful
        if (!getResult.isSuccess()) {
            String errorMsg = getResult.getErrorMessage() != null ? getResult.getErrorMessage() : "Unknown error";
            SessionResult result = new SessionResult();
            result.setSuccess(false);
            result.setErrorMessage("Failed to get session " + sessionId + ": " + errorMsg);
            result.setRequestId(getResult.getRequestId());
            return result;
        }

        // Create the Session object
        Session session = new Session(sessionId, this, new SessionParams());

        // Set ResourceUrl from GetSession response
        if (getResult.getData() != null) {
            GetSessionData data = getResult.getData();
            session.setResourceUrl(data.getResourceUrl());
            
            // TODO: VPC functionality temporarily disabled
            /*
            if (data.isVpcResource()) {
                session.setHttpPort(data.getHttpPort());
                session.setToken(data.getToken());
                session.setNetworkInterfaceIp(data.getNetworkInterfaceIp());
            }
            */
        }

        // Create a default context for file transfer operations for the recovered session
        try {
            String contextName = "file-transfer-context-" + System.currentTimeMillis() / 1000;
            com.aliyun.agentbay.context.ContextResult contextResult = 
                getContextService().get(contextName, true);
            if (contextResult.isSuccess() && contextResult.getContext() != null) {
                session.setFileTransferContextId(contextResult.getContext().getContextId());
            } else {
            }
        } catch (Exception e) {
        }

        SessionResult result = new SessionResult();
        result.setRequestId(getResult.getRequestId());
        result.setSuccess(true);
        result.setSession(session);
        return result;
    }

    /**
     * Remove a session from the cache
     *
     * @param sessionId The session ID to remove
     */
    public void removeSession(String sessionId) {
        sessions.remove(sessionId);
    }

    /**
     * Get the API client
     *
     * @return ApiClient instance
     */
    public ApiClient getApiClient() {
        return apiClient;
    }

    /**
     * Get the underlying OpenAPI client
     *
     * @return Client instance
     */
    public Client getClient() {
        return client;
    }

    /**
     * Get the API key
     *
     * @return The API key
     */
    public String getApiKey() {
        return apiKey;
    }

    /**
     * Get the region ID
     *
     * @return The region ID
     */
    public String getRegionId() {
        return regionId;
    }

    /**
     * Create a new session with CreateSessionParams
     *
     * @param params Parameters for creating the session
     * @return SessionResult containing the created session information
     * @throws AgentBayException if the session creation fails
     */
    public SessionResult create(CreateSessionParams params) throws AgentBayException {
        try {
            if (params == null) {
                params = new CreateSessionParams();
            }
            CreateMcpSessionRequest request = new CreateMcpSessionRequest();
            request.authorization = "Bearer " + apiKey;

            // Handle context syncs
            if (params.getContextSyncs() != null && !params.getContextSyncs().isEmpty()) {
                List<CreateMcpSessionRequest.CreateMcpSessionRequestPersistenceDataList> persistenceDataList =
                    new ArrayList<>();

                for (ContextSync cs : params.getContextSyncs()) {
                    String policyJson = null;
                    if (cs.getPolicy() != null) {
                        try {
                            // Convert policy to Map first, then to JSON
                            Map<String, Object> policyMap = cs.getPolicy().toMap();
                            policyJson = objectMapper.writeValueAsString(policyMap);
                        } catch (Exception e) {
                        }
                    }

                    CreateMcpSessionRequest.CreateMcpSessionRequestPersistenceDataList persistenceData =
                        new CreateMcpSessionRequest.CreateMcpSessionRequestPersistenceDataList();
                    persistenceData.setContextId(cs.getContextId());
                    persistenceData.setPath(cs.getPath());
                    persistenceData.setPolicy(policyJson);

                    persistenceDataList.add(persistenceData);
                }

                request.setPersistenceDataList(persistenceDataList);
            }

            // Add BrowserContext as a ContextSync if provided
            if (params.getBrowserContext() != null) {
                BrowserContext browserContext = params.getBrowserContext();
                
                // Create a new SyncPolicy with default values for browser context
                UploadPolicy uploadPolicy = new UploadPolicy(
                    browserContext.isAutoUpload(),
                    UploadStrategy.UPLOAD_BEFORE_RESOURCE_RELEASE,
                    30
                );
                
                // Create BWList with white lists for browser data paths
                List<WhiteList> whiteLists = new ArrayList<>();
                whiteLists.add(new WhiteList("/Local State", new ArrayList<>()));
                whiteLists.add(new WhiteList("/Default/Cookies", new ArrayList<>()));
                whiteLists.add(new WhiteList("/Default/Cookies-journal", new ArrayList<>()));
                BWList bwList = new BWList(whiteLists);
                
                SyncPolicy syncPolicy = new SyncPolicy(
                    uploadPolicy,
                    DownloadPolicy.defaultPolicy(),
                    DeletePolicy.defaultPolicy(),
                    ExtractPolicy.defaultPolicy(),
                    RecyclePolicy.defaultPolicy(),
                    bwList
                );
                
                // Serialize the sync_policy to JSON
                String policyJson = null;
                try {
                    Map<String, Object> policyMap = syncPolicy.toMap();
                    policyJson = objectMapper.writeValueAsString(policyMap);
                } catch (Exception e) {
                }
                
                // Create browser context sync item
                CreateMcpSessionRequest.CreateMcpSessionRequestPersistenceDataList browserContextSync =
                    new CreateMcpSessionRequest.CreateMcpSessionRequestPersistenceDataList();
                browserContextSync.setContextId(browserContext.getContextId());
                browserContextSync.setPath(com.aliyun.agentbay.Config.BROWSER_DATA_PATH);
                browserContextSync.setPolicy(policyJson);
                
                // Add to persistence data list or create new one if not exists
                if (request.getPersistenceDataList() == null) {
                    request.setPersistenceDataList(new ArrayList<>());
                }
                request.getPersistenceDataList().add(browserContextSync);
                for (int i = 0; i < request.getPersistenceDataList().size(); i++) {
                    CreateMcpSessionRequest.CreateMcpSessionRequestPersistenceDataList item = 
                        request.getPersistenceDataList().get(i);

                }
            }

            // Set image ID if provided
            if (params.getImageId() != null) {
                request.setImageId(params.getImageId());
            }
            
            // Set labels if provided
            if (params.getLabels() != null && !params.getLabels().isEmpty()) {
                try {
                    String labelsJson = objectMapper.writeValueAsString(params.getLabels());
                    request.setLabels(labelsJson);
                } catch (Exception e) {
                }
            }

            // Set policy ID if provided
            if (params.getPolicyId() != null && !params.getPolicyId().isEmpty()) {
                request.setMcpPolicyId(params.getPolicyId());
            }

            // Set network ID if provided
            if (params.getNetworkId() != null && !params.getNetworkId().isEmpty()) {
                request.setNetworkId(params.getNetworkId());
            }

            // Set enable_browser_replay if explicitly set to false
            // Browser replay is enabled by default, so only set when explicitly False
            if (params.getEnableBrowserReplay() != null && !params.getEnableBrowserReplay()) {
                request.setEnableRecord(false);
            }

            // Note: ExtraConfigs is handled automatically by MobileExtraConfig during session creation
            // The mobile configuration will be applied after session is created
            // See: session.getMobile().configure() call below

            // Add SDK stats for tracking
            String framework = params.getFramework() != null ? params.getFramework() : "";
            String sdkStatsJson = String.format(
                "{\"source\":\"sdk\",\"sdk_language\":\"%s\",\"sdk_version\":\"%s\",\"is_release\":%s,\"framework\":\"%s\"}",
                Version.getSdkLanguage(),
                Version.getVersionString(),
                Version.isRelease(),
                framework
            );
            request.setSdkStats(sdkStatsJson);
            CreateMcpSessionResponse response = client.createMcpSession(request);

            if (response == null || response.getBody() == null) {
                String requestId = response != null ? ResponseUtil.extractRequestId(response) : "";
                SessionResult result = new SessionResult();
                result.setSuccess(false);
                result.setErrorMessage("Invalid response from create session API");
                result.setRequestId(requestId);
                return result;
            }

            SessionResult result = new SessionResult();

            // Extract session ID from response data
            String sessionId = null;
            if (response.getBody().getData() != null) {
                // The getData() returns the session data object, we need to extract SessionId
                try {
                    sessionId = response.getBody().getData().getSessionId();
                } catch (Exception e) {
                    sessionId = response.getBody().getData().toString();
                }
            }

            if (sessionId == null || sessionId.isEmpty()) {
                String requestId = ResponseUtil.extractRequestId(response);
                result.setSuccess(false);
                result.setErrorMessage("SessionId not found in response");
                result.setRequestId(requestId);
                return result;
            }

            result.setSessionId(sessionId);
            result.setStatus("created");
            result.setRequestId(ResponseUtil.extractRequestId(response));
            result.setBrowserType(params.getBrowserType());
            result.setSuccess(true);

            // Create and cache the session
            SessionParams sessionParams = new SessionParams();
            sessionParams.setBrowserType(params.getBrowserType());
            Session session = new Session(result.getSessionId(), this, sessionParams);

            // Set browser recording state (default to True if not explicitly set to False)
            session.setEnableBrowserReplay(params.getEnableBrowserReplay() != null ? params.getEnableBrowserReplay() : true);

            // Set VPC-related fields if this is a VPC session
            /*if (response.getBody().getData() != null) {
                boolean vpcResource = (response.getBody().getData().getHttpPort() != null && !response.getBody().getData().getHttpPort().isEmpty());
                if (vpcResource) {
                    session.setHttpPort(response.getBody().getData().getHttpPort());
                    session.updateVpcLinkUrl();
                    session.setToken(response.getBody().getData().getToken());
                    try {
                        session.listMcpTools();
                    } catch (Exception e) {
                    }
                }
            }*/

            sessions.put(result.getSessionId(), session);
            result.setSession(session);

            // Process mobile configuration if provided
            if (params.getExtraConfigs() != null && params.getExtraConfigs().getMobile() != null) {
                try {
                    session.getMobile().configure(params.getExtraConfigs().getMobile());
                } catch (Exception e) {
                }
            }

            // If we have persistence data, wait for context synchronization
            boolean needsContextSync = (params.getContextSyncs() != null && !params.getContextSyncs().isEmpty()) ||
                                      (params.getBrowserContext() != null);
            if (needsContextSync) {
                waitForContextSynchronization(session);
            }

            // Handle mobile simulate if configured
            if (params.getExtraConfigs() != null && 
                params.getExtraConfigs().getMobile() != null &&
                params.getExtraConfigs().getMobile().getSimulateConfig() != null) {
                
                MobileSimulateConfig simConfig = params.getExtraConfigs().getMobile().getSimulateConfig();
                if (simConfig.isSimulate() && simConfig.getSimulatePath() != null) {
                    waitForMobileSimulate(session, simConfig);
                }
            }
            return result;
        } catch (Exception e) {
            SessionResult result = new SessionResult();
            result.setSuccess(false);
            result.setErrorMessage(e.getMessage());
            // Try to extract requestId if exception has it (for ClientException cases)
            if (e instanceof com.aliyun.tea.TeaException) {
                com.aliyun.tea.TeaException teaException = (com.aliyun.tea.TeaException) e;
                if (teaException.getData() != null && teaException.getData().get("RequestId") != null) {
                    result.setRequestId(teaException.getData().get("RequestId").toString());
                }
            }
            return result;
        }
    }

    /**
     * Wait for mobile simulate to complete
     *
     * @param session The session to wait for mobile simulate
     * @param simConfig Mobile simulate configuration
     */
    private void waitForMobileSimulate(Session session, MobileSimulateConfig simConfig) {
        String mobileSimPath = simConfig.getSimulatePath();
        MobileSimulateMode mobileSimMode = simConfig.getSimulateMode();
        
        if (mobileSimPath == null || mobileSimPath.isEmpty()) {
            return;
        }
        
        try {
            long startTime = System.currentTimeMillis();
            String devInfoFilePath = mobileSimPath + "/dev_info.json";
            String wyaApplyOption = "";
            
            if (mobileSimMode == null || mobileSimMode == MobileSimulateMode.PROPERTIES_ONLY) {
                wyaApplyOption = "";
            } else if (mobileSimMode == MobileSimulateMode.SENSORS_ONLY) {
                wyaApplyOption = "-sensors";
            } else if (mobileSimMode == MobileSimulateMode.PACKAGES_ONLY) {
                wyaApplyOption = "-packages";
            } else if (mobileSimMode == MobileSimulateMode.SERVICES_ONLY) {
                wyaApplyOption = "-services";
            } else if (mobileSimMode == MobileSimulateMode.ALL) {
                wyaApplyOption = "-all";
            }
            
            String command = String.format("chmod -R a+rwx %s; wya apply %s %s", 
                                          mobileSimPath, wyaApplyOption, devInfoFilePath).trim();
            com.aliyun.agentbay.model.CommandResult cmdResult = session.getCommand().executeCommand(command, 300000);
            if (cmdResult.isSuccess()) {
                long endTime = System.currentTimeMillis();
                double consumeTime = (endTime - startTime) / 1000.0;
                String modeStr = mobileSimMode != null ? mobileSimMode.getValue() : "PropertiesOnly";
                if (cmdResult.getOutput() != null && !cmdResult.getOutput().isEmpty()) {
                }
            } else {
            }
        } catch (Exception e) {
        }
    }

    /**
     * Wait for context synchronization to complete
     *
     * @param session The session to wait for context synchronization
     */
    private void waitForContextSynchronization(Session session) {
        // Wait for context synchronization to complete
        int maxRetries = 150; // Maximum number of retries
        int retryInterval = 2000; // 2 seconds in milliseconds

        for (int retry = 0; retry < maxRetries; retry++) {
            try {
                // Get context status data
                com.aliyun.agentbay.context.ContextInfoResult infoResult = session.getContext().info();

                // Check if all context items have status "Success" or "Failed"
                boolean allCompleted = true;
                boolean hasFailure = false;

                for (com.aliyun.agentbay.context.ContextStatusData item : infoResult.getContextStatusData()) {
                    if (!"Success".equals(item.getStatus()) && !"Failed".equals(item.getStatus())) {
                        allCompleted = false;
                        break;
                    }

                    if ("Failed".equals(item.getStatus())) {
                        hasFailure = true;
                    }
                }

                if (allCompleted || infoResult.getContextStatusData().isEmpty()) {
                    if (hasFailure) {
                    } else {
                    }
                    break;
                }
                Thread.sleep(retryInterval);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                break;
            } catch (Exception e) {
                try {
                    Thread.sleep(retryInterval);
                } catch (InterruptedException ie) {
                    Thread.currentThread().interrupt();
                    break;
                }
            }
        }
    }

    /**
     * Get context service for this AgentBay instance
     *
     * @return ContextService instance
     */
    public com.aliyun.agentbay.context.ContextService getContextService() {
        return new com.aliyun.agentbay.context.ContextService(this);
    }

    /**
     * Get context service for this AgentBay instance (alias for getContextService)
     *
     * @return ContextService instance
     */
    public com.aliyun.agentbay.context.ContextService getContext() {
        return getContextService();
    }

    /**
     * Get mobile simulate service for this AgentBay instance
     *
     * @return MobileSimulate instance
     */
    public MobileSimulate getMobileSimulate() {
        return mobileSimulate;
    }

    /**
     * Get network service for this AgentBay instance
     *
     * @return Network instance
     */
    public Network getNetwork() {
        return network;
    }

    /**
     * Delete a session
     *
     * @param session The session to delete
     * @param syncContext Whether to sync context before deletion
     * @return DeleteResult
     */
    public com.aliyun.agentbay.model.DeleteResult delete(Session session, boolean syncContext) {
        if (session == null) {
            return new com.aliyun.agentbay.model.DeleteResult("", false, "Session is null");
        }

        com.aliyun.agentbay.model.DeleteResult result = session.delete(syncContext);

        // Remove from sessions map
        sessions.remove(session.getSessionId());

        return result;
    }

}