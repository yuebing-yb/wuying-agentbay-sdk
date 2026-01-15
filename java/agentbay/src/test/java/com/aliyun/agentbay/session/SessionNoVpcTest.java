package com.aliyun.agentbay.session;

import org.junit.Test;

import static org.junit.Assert.fail;

public class SessionNoVpcTest {

    @Test
    public void testSessionDoesNotExposeVpcMethods() {
        assertNoMethod(Session.class, "isVpcEnabled");
        assertNoMethod(Session.class, "getHttpPort");
        assertNoMethod(Session.class, "setHttpPort", String.class);
        assertNoMethod(Session.class, "getNetworkInterfaceIp");
        assertNoMethod(Session.class, "setNetworkInterfaceIp", String.class);
    }

    private static void assertNoMethod(Class<?> clazz, String name, Class<?>... parameterTypes) {
        try {
            clazz.getDeclaredMethod(name, parameterTypes);
            fail("Expected no method: " + name);
        } catch (NoSuchMethodException e) {
            // expected
        }
    }
}

