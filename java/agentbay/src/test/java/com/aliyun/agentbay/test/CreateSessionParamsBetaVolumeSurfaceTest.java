package com.aliyun.agentbay.test;

import com.aliyun.agentbay.session.CreateSessionParams;
import com.aliyun.agentbay.volume.Volume;
import org.junit.Test;

import java.lang.reflect.Method;

import static org.junit.Assert.*;

public class CreateSessionParamsBetaVolumeSurfaceTest {

    @Test
    public void testCreateSessionParamsExposesBetaVolumeAccessors() throws Exception {
        Method get = CreateSessionParams.class.getMethod("getBetaVolume");
        Method set = CreateSessionParams.class.getMethod("setBetaVolume", Volume.class);
        assertNotNull(get);
        assertNotNull(set);
    }

    @Test
    public void testCreateSessionParamsDoesNotExposeLegacyVolumeAccessors() {
        try {
            CreateSessionParams.class.getMethod("getVolume");
            fail("expected CreateSessionParams.getVolume() to be removed; use getBetaVolume() instead");
        } catch (NoSuchMethodException expected) {
            // Expected: legacy accessors are removed.
        }

        try {
            CreateSessionParams.class.getMethod("setVolume", Volume.class);
            fail("expected CreateSessionParams.setVolume(Volume) to be removed; use setBetaVolume(Volume) instead");
        } catch (NoSuchMethodException expected) {
            // Expected: legacy accessors are removed.
        }
    }

    @Test
    public void testCreateSessionParamsDoesNotExposeLegacyVolumeIdAccessors() {
        try {
            CreateSessionParams.class.getMethod("getVolumeId");
            fail("expected CreateSessionParams.getVolumeId() to be removed; use getBetaVolumeId() instead");
        } catch (NoSuchMethodException expected) {
            // Expected: legacy accessors are removed.
        }

        try {
            CreateSessionParams.class.getMethod("setVolumeId", String.class);
            fail("expected CreateSessionParams.setVolumeId(String) to be removed; use setBetaVolumeId(String) instead");
        } catch (NoSuchMethodException expected) {
            // Expected: legacy accessors are removed.
        }
    }
}

