package com.aliyun.agentbay.filesystem;

import com.aliyun.agentbay.model.FileChangeEvent;
import com.aliyun.agentbay.model.FileChangeResult;
import org.junit.Test;

import java.util.*;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicInteger;

import static org.junit.Assert.*;

public class FileSystemWatchTest {

    @Test
    public void testFileChangeEventFromDict() {
        Map<String, Object> dict = new HashMap<>();
        dict.put("eventType", "create");
        dict.put("path", "/tmp/test.txt");
        dict.put("pathType", "file");

        FileChangeEvent event = FileChangeEvent.fromDict(dict);
        assertEquals("create", event.getEventType());
        assertEquals("/tmp/test.txt", event.getPath());
        assertEquals("file", event.getPathType());
    }

    @Test
    public void testFileChangeEventFromDictMissingFields() {
        Map<String, Object> dict = new HashMap<>();
        dict.put("eventType", "modify");

        FileChangeEvent event = FileChangeEvent.fromDict(dict);
        assertEquals("modify", event.getEventType());
        assertEquals("", event.getPath());
        assertEquals("", event.getPathType());
    }

    @Test
    public void testFileChangeResultHasChanges() {
        List<FileChangeEvent> events = Arrays.asList(
            new FileChangeEvent("create", "/tmp/f.txt", "file")
        );
        FileChangeResult result = new FileChangeResult("req-1", true, events, "[]", "");
        assertTrue(result.hasChanges());

        FileChangeResult empty = new FileChangeResult("req-2", true, new ArrayList<>(), "[]", "");
        assertFalse(empty.hasChanges());
    }

    @Test
    public void testFileChangeResultGetModifiedFiles() {
        List<FileChangeEvent> events = Arrays.asList(
            new FileChangeEvent("create", "/tmp/a.txt", "file"),
            new FileChangeEvent("modify", "/tmp/b.txt", "file"),
            new FileChangeEvent("modify", "/tmp/dir", "directory"),
            new FileChangeEvent("delete", "/tmp/c.txt", "file"),
            new FileChangeEvent("modify", "/tmp/d.txt", "file")
        );
        FileChangeResult result = new FileChangeResult("r", true, events, "", "");
        List<String> modified = result.getModifiedFiles();
        assertEquals(Arrays.asList("/tmp/b.txt", "/tmp/d.txt"), modified);
    }

    @Test
    public void testFileChangeResultGetCreatedFiles() {
        List<FileChangeEvent> events = Arrays.asList(
            new FileChangeEvent("create", "/tmp/a.txt", "file"),
            new FileChangeEvent("modify", "/tmp/b.txt", "file"),
            new FileChangeEvent("create", "/tmp/dir", "directory"),
            new FileChangeEvent("create", "/tmp/c.txt", "file")
        );
        FileChangeResult result = new FileChangeResult("r", true, events, "", "");
        List<String> created = result.getCreatedFiles();
        assertEquals(Arrays.asList("/tmp/a.txt", "/tmp/c.txt"), created);
    }

    @Test
    public void testFileChangeResultGetDeletedFiles() {
        List<FileChangeEvent> events = Arrays.asList(
            new FileChangeEvent("create", "/tmp/a.txt", "file"),
            new FileChangeEvent("delete", "/tmp/b.txt", "file"),
            new FileChangeEvent("delete", "/tmp/dir", "directory"),
            new FileChangeEvent("delete", "/tmp/c.txt", "file")
        );
        FileChangeResult result = new FileChangeResult("r", true, events, "", "");
        List<String> deleted = result.getDeletedFiles();
        assertEquals(Arrays.asList("/tmp/b.txt", "/tmp/c.txt"), deleted);
    }

    @Test
    public void testFileChangeEventEquals() {
        FileChangeEvent a = new FileChangeEvent("create", "/tmp/f.txt", "file");
        FileChangeEvent b = new FileChangeEvent("create", "/tmp/f.txt", "file");
        FileChangeEvent c = new FileChangeEvent("modify", "/tmp/f.txt", "file");
        assertEquals(a, b);
        assertNotEquals(a, c);
    }

    @Test
    public void testFileChangeEventToString() {
        FileChangeEvent e = new FileChangeEvent("modify", "/tmp/test.txt", "file");
        String s = e.toString();
        assertTrue(s.contains("modify"));
        assertTrue(s.contains("/tmp/test.txt"));
        assertTrue(s.contains("file"));
    }
}
