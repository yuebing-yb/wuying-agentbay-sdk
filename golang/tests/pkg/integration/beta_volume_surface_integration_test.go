package integration_test

import (
	"reflect"
	"testing"

	mcp "github.com/aliyun/wuying-agentbay-sdk/golang/api/client"
	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
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

func TestCreateSessionParamsHasBetaVolumeSurface(t *testing.T) {
	paramsType := reflect.TypeOf(&agentbay.CreateSessionParams{})
	if _, ok := paramsType.Elem().FieldByName("BetaVolume"); !ok {
		t.Fatalf("expected CreateSessionParams to have field BetaVolume")
	}
	if _, ok := paramsType.Elem().FieldByName("BetaVolumeId"); !ok {
		t.Fatalf("expected CreateSessionParams to have field BetaVolumeId")
	}
	if _, ok := paramsType.Elem().FieldByName("VolumeId"); ok {
		t.Fatalf("expected CreateSessionParams to not have legacy field VolumeId")
	}

	if _, ok := paramsType.MethodByName("WithBetaVolume"); !ok {
		t.Fatalf("expected CreateSessionParams to have method WithBetaVolume")
	}
	if _, ok := paramsType.MethodByName("WithBetaVolumeId"); !ok {
		t.Fatalf("expected CreateSessionParams to have method WithBetaVolumeId")
	}
	if _, ok := paramsType.MethodByName("WithVolumeId"); ok {
		t.Fatalf("expected CreateSessionParams to not have legacy method WithVolumeId")
	}
}
