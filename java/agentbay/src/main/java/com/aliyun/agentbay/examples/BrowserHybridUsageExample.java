package com.aliyun.agentbay.examples;

import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ExecutionException;

import com.aliyun.agentbay.AgentBay;
import com.aliyun.agentbay.browser.BrowserOperator;
import com.aliyun.agentbay.browser.BrowserOption;
import com.aliyun.agentbay.browser.ExtractOptions;
import com.aliyun.agentbay.model.ExecutionResult;
import com.aliyun.agentbay.model.SessionResult;
import com.aliyun.agentbay.session.CreateSessionParams;
import com.aliyun.agentbay.session.Session;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.microsoft.playwright.BrowserContext;
import com.microsoft.playwright.Page;
import com.microsoft.playwright.Playwright;

/**
 * ⚠️ This is a BETA feature
 * Example demonstrating how to perform tasks with a hybrid usage of playwright,
 * browser operator and browser agent, who shares the same browser instance.
 *
 * This example shows how to:
 * 1. Use playwright to launch a browser
 * 2. Execute browser tasks with natural language (Browser Agent)
 * 3. Use browser operator to perform a specific action.
 * 4. All the actions are on the same browser instance
 */
public class BrowserHybridUsageExample {
    public static class WeatherSchema {
        @JsonProperty(value = "city", required = true)
        private String city;
        @JsonProperty(value = "weather", required = true)
        private String weather;

        public String getCity() {
            return this.city;
        }

        public void setCity(String city) {
            this.city = city;
        }

        public String getWeather() {
            return this.weather;
        }

        public void setWeather(String weather) {
            this.weather = weather;
        }
    }

    /**
     * Simple product data model for testing extraction
     */
    public static class ExtractSchema {
        @JsonProperty("title")
        private String title;
    
        public String getTitle() {
            return title;
        }

        public void setTitle(String title) {
            this.title = title;
        }
    }

    public static void main(String[] args) throws Exception {
        System.out.println("=== Running browser hybrid usage example ===\n");
        // 在另一个线程中异步创建 Playwright
        CompletableFuture<Playwright> playwrightFuture = CompletableFuture.supplyAsync(() -> {
            Playwright pw = Playwright.create();
            System.out.println("Playwright created successfully...");
            return pw;
        });

        AgentBay agentBay = new AgentBay("akm-xxx");
        Session session = null;
        try {
            // Create a browser session
            System.out.println("Creating browser session...");
            CreateSessionParams params = new CreateSessionParams();
            params.setImageId("browser_latest");

            SessionResult sessionResult = agentBay.create(params);
            if (!sessionResult.isSuccess() || sessionResult.getSession() == null) {
                System.err.println("Failed to create session: " + sessionResult.getErrorMessage());
                return;
            }

            session = sessionResult.getSession();
            System.out.println("Session Resource URL: " + session.getResourceUrl());
            // Initialize browser
            session.getBrowser().initialize(new BrowserOption());
            String endpointUrl = session.getBrowser().getEndpointUrl();
            System.out.println("Browser endpoint URL: " + endpointUrl);
            // 等待 Playwright 异步创建完成，确保在使用前已经就绪
            Playwright playwright;
            try {
                playwright = playwrightFuture.get(); // 阻塞等待异步任务完成
            } catch (InterruptedException | ExecutionException e) {
                System.err.println("Failed to create Playwright: " + e.getMessage());
                return;
            }
            
            BrowserContext context = null;
            Page page = null;
            com.microsoft.playwright.Browser browser = null;
            try {
                browser = playwright.chromium().connectOverCDP(endpointUrl);
                context = browser.contexts().get(0);
                page = context.newPage();
                // Navigate to a website
                page.navigate("https://www.baidu.com");
                // Wait for page load
                page.waitForTimeout(2000);
                String title = page.title();
                System.out.println("Title of current page: " + title);
                
                // 使用BrowserAgent来执行天气查询任务
                String task = "在百度查询上海天气";
                System.out.println("\nExecuting task: " + task);

                ExecutionResult result = session.getAgent().getBrowser()
                        .executeTaskAndWait(task, 180, true, WeatherSchema.class, true);

                if (result.isSuccess()) {
                    System.out.println("✅ Task completed successfully!");
                    System.out.println("Task ID: " + result.getTaskId());
                    System.out.println("Task Status: " + result.getTaskStatus());
                    System.out.println("Task Result: " + result.getTaskResult());
                } else {
                    System.err.println("❌ Task failed: " + result.getErrorMessage());
                }
                
                // 使用 Browser Operator 提取数据
                String instruction = "Extract page title";
                page = context.pages().get(0);
                ExtractOptions<ExtractSchema> options = new ExtractOptions<>(instruction, ExtractSchema.class);
                options.setUseTextExtract(true);
                BrowserOperator.ExtractResultTuple<ExtractSchema> syncResult = session.getBrowser().getOperator()
                        .extract(page, options);
                ExtractSchema extraction = syncResult.getData();
                System.out.println("Extracted data: " + extraction.getTitle());
                
            } catch (Exception e) {
                System.err.println("Playwright integration failed: " + e.getMessage());
                e.printStackTrace();
            } finally {
                if (page != null) {
                    page.close();
                }
                if (browser != null) {
                    browser.close();
                }
            }
            
        } catch (Exception e) {
            System.err.println("Error: " + e.getMessage());
            e.printStackTrace();
        } finally {
            if (session != null) {
                System.out.println("\nCleaning up session...");
                agentBay.delete(session, false);
            }
        }
    }
}
