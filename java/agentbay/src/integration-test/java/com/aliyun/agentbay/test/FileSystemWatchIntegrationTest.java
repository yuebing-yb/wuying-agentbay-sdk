// ci-stable
package com.aliyun.agentbay.test;

import com.aliyun.agentbay.AgentBay;
import com.aliyun.agentbay.filesystem.FileSystem;
import com.aliyun.agentbay.model.BoolResult;
import com.aliyun.agentbay.model.FileChangeEvent;
import com.aliyun.agentbay.model.SessionResult;
import com.aliyun.agentbay.session.CreateSessionParams;
import com.aliyun.agentbay.session.Session;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicBoolean;

import static org.junit.Assert.*;

/**
 * Integration test for FileSystem.watchDirectory.
 * Requires AGENTBAY_API_KEY environment variable.
 */
public class FileSystemWatchIntegrationTest {

    private AgentBay agentBay;
    private Session session;
    private FileSystem fs;

    @Before
    public void setUp() throws Exception {
        String apiKey = System.getenv("AGENTBAY_API_KEY");
        assertNotNull("AGENTBAY_API_KEY must be set", apiKey);
        assertFalse("AGENTBAY_API_KEY must not be empty", apiKey.isEmpty());

        agentBay = new AgentBay(apiKey);
        SessionResult result = agentBay.create(new CreateSessionParams());
        session = result.getSession();
        assertNotNull("Session must be created", session);
        fs = session.getFileSystem();
    }

    @After
    public void tearDown() {
        if (session != null) {
            try {
                session.delete();
            } catch (Exception ignored) {
            }
        }
    }

    @Test
    public void testWatchDirectoryNoEventsAfterStop() throws Exception {
        String testDir = "/tmp/watch_stop_test_java_" + System.currentTimeMillis();

        System.out.println("=== Testing no events after stop ===");

        System.out.println("1. Creating test directory...");
        BoolResult mkdirResult = fs.createDirectory(testDir);
        assertTrue("Directory creation should succeed", mkdirResult.isSuccess());

        List<FileChangeEvent> allEvents = Collections.synchronizedList(new ArrayList<>());
        AtomicBoolean stop = new AtomicBoolean(false);

        FileSystem.WatchHandle handle = fs.watchDirectory(
            testDir,
            events -> {
                System.out.printf("🔔 Callback triggered with %d events%n", events.size());
                allEvents.addAll(events);
            },
            stop
        );

        assertTrue("Ready should be signaled within 30s", handle.awaitReady(30, TimeUnit.SECONDS));
        System.out.println("✅ Monitoring started");

        System.out.println("\n2. Creating a file (should trigger events)...");
        BoolResult writeResult = fs.writeFile(testDir + "/before_stop.txt", "before stop");
        assertTrue("Write should succeed", writeResult.isSuccess());
        Thread.sleep(3000);

        int eventsBeforeStop = allEvents.size();
        System.out.printf("Events before stop: %d%n", eventsBeforeStop);
        assertTrue("Should detect at least 1 event before stop", eventsBeforeStop > 0);

        System.out.println("\n3. Stopping directory monitoring...");
        stop.set(true);
        handle.join(10_000);
        System.out.println("✅ Monitoring stopped");

        System.out.println("\n4. Creating a file AFTER stop (should NOT trigger events)...");
        BoolResult writeAfter = fs.writeFile(testDir + "/after_stop.txt", "after stop");
        assertTrue("Write should succeed", writeAfter.isSuccess());
        Thread.sleep(3000);

        int eventsAfterStop = allEvents.size();
        int newEvents = eventsAfterStop - eventsBeforeStop;
        System.out.printf("Events after stop: %d, new: %d%n", eventsAfterStop, newEvents);

        assertEquals("Should have 0 new events after stop", 0, newEvents);
        System.out.println("✅ No events after stop — negative verification passed!");
    }

    @Test
    public void testWatchDirectoryDetectsEvents() throws Exception {
        String watchDir = "/tmp/watch_test_java_integration";

        // 1. Create the test directory
        System.out.println("1. Creating test directory...");
        BoolResult mkdirResult = fs.createDirectory(watchDir);
        assertTrue("Directory creation should succeed", mkdirResult.isSuccess());

        // 2. Start watching
        System.out.println("2. Starting directory monitoring...");
        List<FileChangeEvent> allEvents = Collections.synchronizedList(new ArrayList<>());
        List<Integer> callbackSizes = Collections.synchronizedList(new ArrayList<>());

        AtomicBoolean stop = new AtomicBoolean(false);
        FileSystem.WatchHandle handle = fs.watchDirectory(
            watchDir,
            events -> {
                System.out.printf("\uD83D\uDD14 Callback triggered with %d events:%n", events.size());
                callbackSizes.add(events.size());
                for (FileChangeEvent e : events) {
                    System.out.printf("   - %s: %s (%s)%n", e.getEventType(), e.getPath(), e.getPathType());
                }
                allEvents.addAll(events);
            },
            stop
        );

        assertTrue("Ready should be signaled within 30s", handle.awaitReady(30, TimeUnit.SECONDS));
        System.out.println("\u2705 Directory monitoring started (baseline established)");

        // 3. Create a new file
        System.out.println("3. Creating a new file...");
        BoolResult writeResult = fs.writeFile(watchDir + "/test1.txt", "hello world");
        assertTrue("Write should succeed", writeResult.isSuccess());
        Thread.sleep(2000);

        // 4. Modify the file
        System.out.println("4. Modifying the file...");
        BoolResult modifyResult = fs.writeFile(watchDir + "/test1.txt", "hello world updated", "overwrite");
        assertTrue("Modify should succeed", modifyResult.isSuccess());
        Thread.sleep(2000);

        // 5. Create another file
        System.out.println("5. Creating another file...");
        BoolResult writeResult2 = fs.writeFile(watchDir + "/test2.txt", "second file");
        assertTrue("Write should succeed", writeResult2.isSuccess());
        Thread.sleep(2000);

        // 6. Stop monitoring
        System.out.println("6. Stopping directory monitoring...");
        stop.set(true);
        handle.join(10_000);
        System.out.println("\u2705 Directory monitoring stopped");

        // Verify results
        System.out.println("\n=== RESULTS ===");
        System.out.printf("Total callback calls: %d%n", callbackSizes.size());
        System.out.printf("Total events detected: %d%n", allEvents.size());
        System.out.printf("Callback call sizes: %s%n", callbackSizes);
        System.out.println("\nDetected events:");
        for (int i = 0; i < allEvents.size(); i++) {
            FileChangeEvent e = allEvents.get(i);
            System.out.printf("  %d. %s: %s (%s)%n", i + 1, e.getEventType(), e.getPath(), e.getPathType());
        }

        assertTrue("Should detect at least 3 events (one per file operation)", allEvents.size() >= 3);

        long createCount = allEvents.stream()
            .filter(e -> "create".equals(e.getEventType()))
            .count();
        long modifyCount = allEvents.stream()
            .filter(e -> "modify".equals(e.getEventType()))
            .count();
        assertTrue("Should have at least 2 create events", createCount >= 2);
        assertTrue("Should have at least 1 modify event", modifyCount >= 1);

        System.out.printf("%nEvent type breakdown:%n");
        System.out.printf("  Create events: %d (expected: >=2)%n", createCount);
        System.out.printf("  Modify events: %d (expected: >=1)%n", modifyCount);
        System.out.println("\u2705 watch_directory integration test completed successfully!");
    }
}
