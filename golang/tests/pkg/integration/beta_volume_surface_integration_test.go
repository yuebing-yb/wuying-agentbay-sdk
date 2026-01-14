package integration_test

import (
	"reflect"
	"testing"

	mcp "github.com/aliyun/wuying-agentbay-sdk/golang/api/client"
)

// These tests are intentionally focused on SDK surface compatibility with the upstream Aliyun TEA SDK.
// They run before the end-to-end beta volume flow tests to keep TDD iterations small.

func TestMcpClientHasVolumeAPIs(t *testing.T) {
	clientType := reflect.TypeOf(&mcp.Client{})
	for _, name := range []string{"GetVolume", "DeleteVolume", "ListVolumes"} {
		if _, ok := clientType.MethodByName(name); !ok {
			t.Fatalf("expected mcp.Client to have method %s", name)
		}
	}
}

func TestCreateMcpSessionRequestHasVolumeIdField(t *testing.T) {
	reqType := reflect.TypeOf(mcp.CreateMcpSessionRequest{})
	if _, ok := reqType.FieldByName("VolumeId"); !ok {
		t.Fatalf("expected CreateMcpSessionRequest to have field VolumeId")
	}
}
