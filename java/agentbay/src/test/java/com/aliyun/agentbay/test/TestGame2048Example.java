package com.aliyun.agentbay.test;

import com.aliyun.agentbay.AgentBay;
import com.aliyun.agentbay.browser.BrowserAgent;
import com.aliyun.agentbay.browser.BrowserOption;
import com.aliyun.agentbay.browser.ExtractOptions;
import com.aliyun.agentbay.exception.AgentBayException;
import com.aliyun.agentbay.model.SessionInfoResult;
import com.aliyun.agentbay.model.SessionResult;
import com.aliyun.agentbay.session.CreateSessionParams;
import com.aliyun.agentbay.session.Session;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.microsoft.playwright.*;
import org.junit.AfterClass;
import org.junit.BeforeClass;
import org.junit.Test;
import java.util.List;

import static org.junit.Assert.*;

/**
 * Test cases for Game2048Example functionality
 * Tests the SDK methods used in the Game2048 example including:
 * - AgentBay client initialization
 * - Session creation and management
 * - Browser initialization and control
 * - Browser agent data extraction
 */
public class TestGame2048Example {
    private static AgentBay agentBay;
    private static Session session;
    private static String apiKey;

    public static class GameState {
        @JsonProperty("score")
        private Integer score;

        @JsonProperty("highestTile")
        private Integer highestTile;

        @JsonProperty("grid")
        private List<List<Integer>> grid;

        public Integer getScore() {
            return score;
        }

        public void setScore(Integer score) {
            this.score = score;
        }

        public Integer getHighestTile() {
            return highestTile;
        }

        public void setHighestTile(Integer highestTile) {
            this.highestTile = highestTile;
        }

        public List<List<Integer>> getGrid() {
            return grid;
        }

        public void setGrid(List<List<Integer>> grid) {
            this.grid = grid;
        }
    }

    @BeforeClass
    public static void setUp() throws AgentBayException {
        apiKey = System.getenv("AGENTBAY_API_KEY");
        assertNotNull("AGENTBAY_API_KEY environment variable must be set", apiKey);
        assertFalse("AGENTBAY_API_KEY cannot be empty", apiKey.trim().isEmpty());
        
        // Initialize AgentBay client for each test
        agentBay = new AgentBay();
        
        // Create session for tests that need it
        CreateSessionParams params = new CreateSessionParams();
        params.setImageId("browser_latest");
        SessionResult sessionResult = agentBay.create(params);
        
        if (sessionResult.isSuccess()) {
            session = sessionResult.getSession();
        } else {
            fail("Failed to create session: " + sessionResult.getErrorMessage());
        }
    }

    @AfterClass
    public static void tearDown() {
        if (session != null) {
            try {
                // Note: Session cleanup is handled automatically by the SDK
            } catch (Exception e) {
            }
        }
    }

    @Test
    public void test01_AgentBayInitialization() {
        assertNotNull("AgentBay client should not be null", agentBay);
    }

    @Test
    public void test02_SessionCreation() {
        assertNotNull("Session should not be null", session);
        assertNotNull("Session ID should not be null", session.getSessionId());
        assertFalse("Session ID should not be empty", session.getSessionId().isEmpty());
    }

    @Test
    public void test03_SessionInfo() throws Exception {
        assertNotNull("Session must be created before testing info", session);
        
        SessionInfoResult result = session.info();
        
        assertNotNull("Session info result should not be null", result);
        assertTrue("Session info retrieval should succeed", result.isSuccess());
        assertNotNull("Session info should not be null", result.getSessionInfo());
        
        String desktopUrl = result.getSessionInfo().getResourceUrl();
        assertNotNull("Desktop URL should not be null", desktopUrl);
        assertFalse("Desktop URL should not be empty", desktopUrl.isEmpty());

    }

    @Test
    public void test04_BrowserInitialization() {
        assertNotNull("Session must be created before testing browser", session);
        assertNotNull("Browser object should not be null", session.getBrowser());
        
        BrowserOption browserOption = new BrowserOption();
        boolean initResult = session.getBrowser().initialize(browserOption);
        
        assertTrue("Browser initialization should succeed", initResult);
    }

    @Test
    public void test05_BrowserEndpointUrl() throws Exception {
        assertNotNull("Session must be created before testing endpoint URL", session);
        assertNotNull("Browser object should not be null", session.getBrowser());
        
        // Initialize browser first
        session.getBrowser().initialize(new BrowserOption());
        
        String endpointUrl = session.getBrowser().getEndpointUrl();
        
        assertNotNull("Endpoint URL should not be null", endpointUrl);
        assertFalse("Endpoint URL should not be empty", endpointUrl.isEmpty());
        assertTrue("Endpoint URL should be a WebSocket URL", 
                   endpointUrl.startsWith("ws://") || endpointUrl.startsWith("wss://"));

    }

    @Test
    public void test06_BrowserAgentAccess() {
        assertNotNull("Session must be created before testing agent", session);
        assertNotNull("Browser object should not be null", session.getBrowser());
        
        // Initialize browser first
        session.getBrowser().initialize(new BrowserOption());
        
        BrowserAgent agent = session.getBrowser().getAgent();
        
        assertNotNull("Browser agent should not be null", agent);
    }

    @Test
    public void test07_BrowserAgentExtract() {
        assertNotNull("Session must be created before testing extract", session);
        
        try {
            // Initialize browser first
            session.getBrowser().initialize(new BrowserOption());
            
            try (Playwright playwright = Playwright.create()) {
                String endpointUrl = session.getBrowser().getEndpointUrl();
                com.microsoft.playwright.Browser browser = playwright.chromium().connectOverCDP(endpointUrl);
                BrowserContext context = browser.contexts().get(0);
                Page page = context.newPage();
                BrowserAgent agent = session.getBrowser().getAgent();
                page.navigate("https://ovolve.github.io/2048-AI/",
                    new Page.NavigateOptions()
                        .setWaitUntil(com.microsoft.playwright.options.WaitUntilState.DOMCONTENTLOADED)
                        .setTimeout(180000));
                Thread.sleep(1000);
                page.waitForSelector(".grid-container", new Page.WaitForSelectorOptions().setTimeout(10000));
                
                // Wait a bit for initial tiles to appear
                Thread.sleep(1000);
                
                String instruction = "Extract the current game state:\n" +
                    "1. Score from the score counter\n" +
                    "2. All tile values and their positions in the 4x4 grid must be extracted. \n" +
                    "    Each tile's value and position can be obtained from the tile-position-x-y class, where x (1 to 4) is the column and y (1 to 4) is the row.\n" +
                    "    For example, tile-position-4-1 means the tile is in column 4, row 1.\n" +
                    "    The value of the tile is given by the number in the tile's class.\n" +
                    "    For example, <div class='tile tile-2 tile-position-1-4 tile-new'>2</div> means a tile with value 2 at column 1, row 4;\n" +
                    "    and <div class='tile tile-2 tile-position-4-1 tile-new'>2</div> means a tile with value 2 at column 4, row 1.\n" +
                    "    Empty spaces should be represented as 0 in the grid.\n" +
                    "    For instance, if the only tiles present are the two above, the grid should be:[[0, 0, 0, 2], [0, 0, 0, 0], [0, 0, 0, 0], [2, 0, 0, 0]]\n" +
                    "3. Highest tile value present";
                ExtractOptions<GameState> extractOptions = new ExtractOptions<>(instruction, GameState.class);
                extractOptions.setUseTextExtract(false);
                
                BrowserAgent.ExtractResultTuple<GameState> extractResult = agent.extract(page, extractOptions);
                
                assertNotNull("Extract result should not be null", extractResult);
                assertTrue("Extract operation should succeed", extractResult.isSuccess());
                
                GameState gameState = extractResult.getData();
                assertNotNull("Game state should not be null", gameState);
                assertNotNull("Grid should not be null", gameState.getGrid());
                assertEquals("Grid should have 4 rows", 4, gameState.getGrid().size());
                
                for (List<Integer> row : gameState.getGrid()) {
                    assertEquals("Each row should have 4 columns", 4, row.size());
                }
                
                assertNotNull("Score should not be null", gameState.getScore());
                assertTrue("Score should be non-negative", gameState.getScore() >= 0);
                
                assertNotNull("Highest tile should not be null", gameState.getHighestTile());
                assertTrue("Highest tile should be positive", gameState.getHighestTile() > 0);

                page.close();
                browser.close();
            }
        } catch (Exception e) {
            fail("Extract operation should not throw exception: " + e.getMessage());
        }
    }

    @Test
    public void test08_KeyboardInteraction() {
        assertNotNull("Session must be created before testing keyboard", session);
        
        try {
            // Initialize browser first
            session.getBrowser().initialize(new BrowserOption());
            
            try (Playwright playwright = Playwright.create()) {
                String endpointUrl = session.getBrowser().getEndpointUrl();
                com.microsoft.playwright.Browser browser = playwright.chromium().connectOverCDP(endpointUrl);
                BrowserContext context = browser.contexts().get(0);
                Page page = context.newPage();
                page.navigate("https://ovolve.github.io/2048-AI/",
                    new Page.NavigateOptions()
                        .setWaitUntil(com.microsoft.playwright.options.WaitUntilState.DOMCONTENTLOADED)
                        .setTimeout(180000));

                Thread.sleep(1000);
                
                page.waitForSelector(".grid-container", new Page.WaitForSelectorOptions().setTimeout(10000));
                Thread.sleep(1000);
                page.keyboard().press("ArrowLeft");
                Thread.sleep(1000);
                
                page.keyboard().press("ArrowUp");
                Thread.sleep(1000);
                page.close();
                browser.close();
            }
        } catch (Exception e) {
            fail("Keyboard interaction should not throw exception: " + e.getMessage());
        }
    }

    @Test
    public void test09_InvalidApiKey() {
        try {
            AgentBay invalidClient = new AgentBay("invalid_api_key");
            CreateSessionParams params = new CreateSessionParams();
            params.setImageId("browser_latest");
            SessionResult result = invalidClient.create(params);
            
            assertFalse("Invalid API key should not create session successfully", result.isSuccess());
            assertNotNull("Error message should be present", result.getErrorMessage());
        } catch (AgentBayException e) {
            // This is expected behavior
        } catch (Exception e) {
            // This is also acceptable
        }
    }

    @Test
    public void test10_ExtractOptionsConfiguration() {
        String instruction = "Extract game state";
        ExtractOptions<GameState> extractOptions = new ExtractOptions<>(instruction, GameState.class);
        
        assertNotNull("Extract options should not be null", extractOptions);
        
        // Test setting useTextExtract
        extractOptions.setUseTextExtract(false);
        // Note: If there's no getter, we can't verify but we can ensure no exception is thrown
        
        extractOptions.setUseTextExtract(true);
        // Note: If there's no getter, we can't verify but we can ensure no exception is thrown
    }
}

