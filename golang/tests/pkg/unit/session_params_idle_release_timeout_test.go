package agentbay_test

import (
	"testing"

	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
	"github.com/stretchr/testify/assert"
)

func TestCreateSessionParams_IdleReleaseTimeout_Default(t *testing.T) {
	params := agentbay.NewCreateSessionParams()
	assert.Equal(t, int32(0), params.IdleReleaseTimeout)
}

func TestCreateSessionParams_IdleReleaseTimeout_Setter(t *testing.T) {
	params := agentbay.NewCreateSessionParams()
	params.WithIdleReleaseTimeout(123)
	assert.Equal(t, int32(123), params.IdleReleaseTimeout)
}
