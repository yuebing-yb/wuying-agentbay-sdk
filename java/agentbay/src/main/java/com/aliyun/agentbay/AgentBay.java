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
import com.aliyun.agentbay.network.BetaNetworkService;
import com.aliyun.agentbay.session.Session;
import com.aliyun.agentbay.session.CreateSessionParams;
import com.aliyun.agentbay.util.ResponseUtil;
import com.aliyun.agentbay.util.Version;
import com.aliyun.agentbay.volume.BetaVolumeService;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.aliyun.teaopenapi.models.Config;
import com.aliyun.wuyingai20250506.Client;
import com.aliyun.wuyingai20250506.models.CreateMcpSessionRequest;
import com.aliyun.wuyingai20250506.models.CreateMcpSessionResponse;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;


/**
 * Main client for interacting with the AgentBay cloud runtime environment
 */

public class AgentBay {
    private static final ObjectMapper objectMapper = new ObjectMapper();
    private static final Logger logger = LoggerFactory.getLogger(AgentBay.class);

    private String apiKey;
    private String regionId;
    public Client client;
    private ApiClient apiClient;
    private ConcurrentHashMap<String, Session> sessions;
    private MobileSimulate mobileSimulate;
    private BetaNetworkService betaNetwork;
    private BetaVolumeService betaVolume;

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
            this.betaNetwork = new BetaNetworkService(this);
            this.betaVolume = new BetaVolumeService(this);
        } catch (Exception e) {
            throw new AgentBayException("Failed to initialize AgentBay client", e);
        }
    }


    /**
     * Get a session by its ID from remote server.
     * This method calls the GetSession API to retrieve session information and creates a Session object.
     * This method fetches from the remote server, enabling session recovery scenarios.
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
        GetSessionResult getResult;
        try {
            com.aliyun.wuyingai20250506.models.GetSessionRequest request =
                new com.aliyun.wuyingai20250506.models.GetSessionRequest();
            request.setAuthorization("Bearer " + apiKey);
            request.setSessionId(sessionId);

            com.aliyun.wuyingai20250506.models.GetSessionResponse response = client.getSession(request);

            String requestId = ResponseUtil.extractRequestId(response);

            if (response == null || response.getBody() == null) {
                getResult = new GetSessionResult(
                    requestId,
                    false,
                    null,
                    "Invalid response from GetSession API"
                );
            } else {
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
                    getResult = new GetSessionResult(
                        requestId,
                        false,
                        null,
                        errorMsg
                    );
                } else {
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
                            body.getCode() != null ? body.getCode() : "",
                            responseData.getToolList()
                        );
                    }

                    getResult = new GetSessionResult(
                        requestId,
                        true,
                        data,
                        ""
                    );
                }
            }
        } catch (com.aliyun.tea.TeaException e) {
            String errorStr = e.getMessage();
            String requestId = "";
            if (e.getData() != null && e.getData().get("RequestId") != null) {
                requestId = e.getData().get("RequestId").toString();
            }

            // Check if this is an expected business error (e.g., session not found)
            if (errorStr != null && (errorStr.contains("InvalidMcpSession.NotFound") ||
                                     errorStr.contains("NotFound"))) {
                getResult = new GetSessionResult(
                    requestId,
                    false,
                    null,
                    "Session " + sessionId + " not found"
                );
            } else {
                getResult = new GetSessionResult(
                    requestId,
                    false,
                    null,
                    "Failed to get session " + sessionId + ": " + errorStr
                );
            }
        } catch (Exception e) {
            getResult = new GetSessionResult(
                "",
                false,
                null,
                "Failed to get session " + sessionId + ": " + e.getMessage()
            );
        }

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
            if (data.getToolList() != null && !data.getToolList().isEmpty()) {
                session.updateMcpTools(data.getToolList());
            }
            
            // TODO: VPC functionality temporarily disabled
            /*
            if (data.isVpcResource()) {
                session.setHttpPort(data.getHttpPort());
                session.setToken(data.getToken());
                session.setNetworkInterfaceIp(data.getNetworkInterfaceIp());
            }
            */
        }

        SessionResult result = new SessionResult();
        result.setRequestId(getResult.getRequestId());
        result.setSuccess(true);
        result.setSession(session);
        return result;
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
     * Get the API client (internal use)
     *
     * @return ApiClient instance
     */
    public ApiClient getApiClient() {
        return apiClient;
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
     * Get beta network service (trial feature).
     *
     * @return BetaNetworkService instance
     */
    public BetaNetworkService getBetaNetwork() {
        return betaNetwork;
    }

    /**
     * Get beta volume service (trial feature).
     *
     * @return BetaVolumeService instance
     */
    public BetaVolumeService getBetaVolume() {
        return betaVolume;
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
            }

            // Set image ID if provided
            if (params.getImageId() != null) {
                request.setImageId(params.getImageId());
            }

            // Beta: mount volume during session creation (static mount only)
            if (params.getVolume() != null && params.getVolume().getId() != null && !params.getVolume().getId().isEmpty()) {
                request.setVolumeId(params.getVolume().getId());
            } else if (params.getVolumeId() != null && !params.getVolumeId().isEmpty()) {
                request.setVolumeId(params.getVolumeId());
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

            // Beta: Set network ID if provided
            if (params.getBetaNetworkId() != null && !params.getBetaNetworkId().isEmpty()) {
                request.setNetworkId(params.getBetaNetworkId());
            }

            // Set enable_browser_replay if explicitly set to false
            // Browser replay is enabled by default, so only set when explicitly False
            if (params.getEnableBrowserReplay() != null && !params.getEnableBrowserReplay()) {
                request.setEnableRecord(false);
            }

            // Note: ExtraConfigs is handled automatically by MobileExtraConfig during session creation
            // The mobile configuration will be applied after session is created
            // See: session.mobile.configure() call below

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

            // Add LoginRegionId if region_id is set
            if (this.regionId != null && !this.regionId.isEmpty()) {
                request.setLoginRegionId(this.regionId);
            }
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
            String requestId = ResponseUtil.extractRequestId(response);
            result.setRequestId(requestId);

            // Check for API-level errors (body.Success and body.Code)
            if (response.getBody().getSuccess() != null && !response.getBody().getSuccess()) {
                String code = response.getBody().getCode() != null ? response.getBody().getCode() : "Unknown";
                String message = response.getBody().getMessage() != null ? response.getBody().getMessage() : "Unknown error";
                result.setSuccess(false);
                result.setErrorMessage(String.format("[%s] %s", code, message));
                return result;
            }

            // Check if data exists
            if (response.getBody().getData() == null) {
                result.setSuccess(false);
                result.setErrorMessage("Invalid response format: 'Data' field is missing");
                return result;
            }

            // Check for data-level errors (data.Success and data.ErrMsg)
            if (response.getBody().getData().getSuccess() != null && !response.getBody().getData().getSuccess()) {
                String errorMsg = response.getBody().getData().getErrMsg() != null ?
                    response.getBody().getData().getErrMsg() : "Session creation failed";
                result.setSuccess(false);
                result.setErrorMessage(errorMsg);
                return result;
            }

            // Extract session ID from response data
            String sessionId = null;
            try {
                sessionId = response.getBody().getData().getSessionId();
            } catch (Exception e) {
            }

            if (sessionId == null || sessionId.isEmpty()) {
                result.setSuccess(false);
                result.setErrorMessage("SessionId not found in response");
                return result;
            }

            result.setSessionId(sessionId);
            result.setStatus("created");
            result.setBrowserType(params.getBrowserType());
            result.setSuccess(true);

            // Create and cache the session
            SessionParams sessionParams = new SessionParams();
            sessionParams.setBrowserType(params.getBrowserType());
            Session session = new Session(result.getSessionId(), this, sessionParams);
            if (params.getImageId() != null) {
                session.setImageId(params.getImageId());
            }

            // Set browser recording state (default to True if not explicitly set to False)
            session.setEnableBrowserReplay(params.getEnableBrowserReplay() != null ? params.getEnableBrowserReplay() : true);

            // LinkUrl/token may be returned by the server for direct tool calls.
            if (response.getBody().getData() != null) {
                if (response.getBody().getData().getToken() != null) {
                    session.setToken(response.getBody().getData().getToken());
                }
                if (response.getBody().getData().getLinkUrl() != null) {
                    session.setLinkUrl(response.getBody().getData().getLinkUrl());
                }
                if (response.getBody().getData().getToolList() != null) {
                    session.updateMcpTools(response.getBody().getData().getToolList());
                }
            }

            sessions.put(result.getSessionId(), session);
            result.setSession(session);

            // Process mobile configuration if provided
            if (params.getExtraConfigs() != null && params.getExtraConfigs().getMobile() != null) {
                try {
                    session.mobile.configure(params.getExtraConfigs().getMobile());
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
                // no-op
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
     * Returns paginated list of sessions filtered by labels.
     *
     * @param labels Labels to filter sessions (optional)
     * @param page Page number for pagination starting from 1 (optional)
     * @param limit Maximum number of items per page (default: 10)
     * @param status Status to filter sessions: RUNNING, PAUSING, PAUSED, RESUMING, DELETING, DELETED (optional)
     * @return SessionListResult containing paginated list of session information
     */
    public com.aliyun.agentbay.model.SessionListResult list(
            java.util.Map<String, String> labels,
            Integer page,
            Integer limit,
            String status) {
        try {
            // Set default values
            if (limit == null) {
                limit = 10;
            }

            // Validate status parameter
            if (status != null && !com.aliyun.agentbay.enums.SessionStatus.isValid(status)) {
                return new com.aliyun.agentbay.model.SessionListResult(
                    "",
                    false,
                    "Invalid status '" + status + "'. Must be one of: RUNNING, PAUSING, PAUSED, RESUMING, DELETING, DELETED",
                    new ArrayList<>(),
                    "",
                    limit,
                    0
                );
            }

            // Validate page number
            if (page != null && page < 1) {
                return new com.aliyun.agentbay.model.SessionListResult(
                    "",
                    false,
                    "Cannot reach page " + page + ": Page number must be >= 1",
                    new ArrayList<>(),
                    "",
                    limit,
                    0
                );
            }

            // Calculate next_token based on page number
            String nextToken = "";
            if (page != null && page > 1) {
                // We need to fetch pages 1 through page-1 to get the next_token
                int currentPage = 1;
                while (currentPage < page) {
                    // Make API call to get next_token
                    String labelsJson = labels != null ? objectMapper.writeValueAsString(labels) : "{}";
                    com.aliyun.wuyingai20250506.models.ListSessionRequest request =
                        new com.aliyun.wuyingai20250506.models.ListSessionRequest();
                    request.setAuthorization("Bearer " + apiKey);
                    request.setLabels(labelsJson);
                    request.setMaxResults(limit);
                    if (nextToken != null && !nextToken.isEmpty()) {
                        request.setNextToken(nextToken);
                    }

                    com.aliyun.wuyingai20250506.models.ListSessionResponse response = client.listSession(request);
                    String requestId = ResponseUtil.extractRequestId(response);
                    com.aliyun.wuyingai20250506.models.ListSessionResponseBody body = response.getBody();

                    if (body == null || !body.getSuccess()) {
                        String errorMessage = body != null ? body.getMessage() : "Unknown error";
                        return new com.aliyun.agentbay.model.SessionListResult(
                            requestId,
                            false,
                            "Cannot reach page " + page + ": " + errorMessage,
                            new ArrayList<>(),
                            "",
                            limit,
                            0
                        );
                    }

                    nextToken = body.getNextToken();
                    if (nextToken == null || nextToken.isEmpty()) {
                        // No more pages available
                        return new com.aliyun.agentbay.model.SessionListResult(
                            requestId,
                            false,
                            "Cannot reach page " + page + ": No more pages available",
                            new ArrayList<>(),
                            "",
                            limit,
                            body.getTotalCount() != null ? body.getTotalCount() : 0
                        );
                    }
                    currentPage++;
                }
            }

            // Make the actual request for the desired page
            String labelsJson = labels != null ? objectMapper.writeValueAsString(labels) : "{}";
            com.aliyun.wuyingai20250506.models.ListSessionRequest request =
                new com.aliyun.wuyingai20250506.models.ListSessionRequest();
            request.setAuthorization("Bearer " + apiKey);
            request.setLabels(labelsJson);
            request.setMaxResults(limit);
            if (nextToken != null && !nextToken.isEmpty()) {
                request.setNextToken(nextToken);
            }

            com.aliyun.wuyingai20250506.models.ListSessionResponse response = client.listSession(request);

            // Extract request ID
            String requestId = ResponseUtil.extractRequestId(response);
            com.aliyun.wuyingai20250506.models.ListSessionResponseBody body = response.getBody();

            // Check for errors in the response
            if (body == null || !body.getSuccess()) {
                String errorMessage = body != null ? body.getMessage() : "Unknown error";
                return new com.aliyun.agentbay.model.SessionListResult(
                    requestId,
                    false,
                    "Failed to list sessions: " + errorMessage,
                    new ArrayList<>(),
                    "",
                    limit,
                    0
                );
            }

            // Extract session data
            List<com.aliyun.agentbay.model.SessionListResult.SessionInfo> sessionInfos = new ArrayList<>();
            if (body.getData() != null) {
                for (com.aliyun.wuyingai20250506.models.ListSessionResponseBody.ListSessionResponseBodyData sessionData : body.getData()) {
                    String sessionId = sessionData.getSessionId();
                    String sessionStatus = sessionData.getSessionStatus();
                    if (sessionId != null) {
                        sessionInfos.add(new com.aliyun.agentbay.model.SessionListResult.SessionInfo(
                            sessionId,
                            sessionStatus != null ? sessionStatus : "UNKNOWN"
                        ));
                    }
                }
            }

            // Return SessionListResult with request ID and pagination info
            return new com.aliyun.agentbay.model.SessionListResult(
                requestId,
                true,
                "",
                sessionInfos,
                body.getNextToken() != null ? body.getNextToken() : "",
                body.getMaxResults() != null ? body.getMaxResults() : limit,
                body.getTotalCount() != null ? body.getTotalCount() : 0
            );

        } catch (Exception e) {
            return new com.aliyun.agentbay.model.SessionListResult(
                "",
                false,
                "Failed to list sessions: " + e.getMessage(),
                new ArrayList<>(),
                "",
                limit != null ? limit : 10,
                0
            );
        }
    }

    /**
     * Returns paginated list of sessions with default parameters.
     *
     * @return SessionListResult containing paginated list of session information
     */
    public com.aliyun.agentbay.model.SessionListResult list() {
        return list(null, null, null, null);
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