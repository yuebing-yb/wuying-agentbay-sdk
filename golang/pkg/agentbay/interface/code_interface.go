package interfaces

import (
	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay/code"
)

//go:generate mockgen -destination=../../../tests/pkg/unit/mock/mock_code.go -package=mock github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay/interface CodeInterface

// CodeInterface defines the interface for code execution operations
type CodeInterface interface {
	// RunCode executes code in the specified language.
	//
	// Optional args may include:
	// - int timeoutS
	RunCode(code string, language string, args ...interface{}) (*code.CodeResult, error)
}
