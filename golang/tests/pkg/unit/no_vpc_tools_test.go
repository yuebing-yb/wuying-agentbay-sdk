package agentbay_test

import (
	"reflect"
	"testing"

	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
)

func TestNoVpcParamsInCreateSessionParams(t *testing.T) {
	t.Run("CreateSessionParams must not expose IsVpc field", func(t *testing.T) {
		typ := reflect.TypeOf(agentbay.CreateSessionParams{})
		if _, ok := typ.FieldByName("IsVpc"); ok {
			t.Fatalf("CreateSessionParams must not have IsVpc field")
		}
	})

	t.Run("CreateSessionParams must not expose WithIsVpc method", func(t *testing.T) {
		typ := reflect.TypeOf(&agentbay.CreateSessionParams{})
		if _, ok := typ.MethodByName("WithIsVpc"); ok {
			t.Fatalf("CreateSessionParams must not have WithIsVpc method")
		}
	})
}

