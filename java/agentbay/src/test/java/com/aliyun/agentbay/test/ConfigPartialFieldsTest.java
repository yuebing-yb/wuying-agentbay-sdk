package com.aliyun.agentbay.test;

import com.aliyun.agentbay.Config;
import org.junit.Test;

import static org.junit.Assert.assertEquals;

public class ConfigPartialFieldsTest {

    @Test
    public void testConfigConstructorWithOnlyRegionIdUsesDefaults() {
        Config cfg = new Config("ap-southeast-1");
        assertEquals("ap-southeast-1", cfg.getRegionId());
        assertEquals("wuyingai.cn-shanghai.aliyuncs.com", cfg.getEndpoint());
        assertEquals(60000, cfg.getTimeoutMs());
    }
}

