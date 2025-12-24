package models

import (
	"encoding/json"
	"fmt"
)

// SessionMetrics represents structured runtime metrics returned by the MCP get_metrics tool.
type SessionMetrics struct {
	CpuCount   int     `json:"cpu_count"`
	CpuUsedPct float64 `json:"cpu_used_pct"`

	DiskTotal int64 `json:"disk_total"`
	DiskUsed  int64 `json:"disk_used"`

	MemTotal int64 `json:"mem_total"`
	MemUsed  int64 `json:"mem_used"`

	RxRateKBps float64 `json:"rx_rate_KBps"`
	TxRateKBps float64 `json:"tx_rate_KBps"`
	RxUsedKB   float64 `json:"rx_used_KB"`
	TxUsedKB   float64 `json:"tx_used_KB"`

	Timestamp string `json:"timestamp"`
}

// SessionMetricsResult represents the result of Session.GetMetrics().
type SessionMetricsResult struct {
	ApiResponse
	Success      bool                   `json:"success"`
	Metrics      *SessionMetrics        `json:"metrics,omitempty"`
	Raw          map[string]interface{} `json:"raw,omitempty"`
	ErrorMessage string                 `json:"error_message,omitempty"`
}

// ParseSessionMetrics parses the MCP get_metrics tool result into a structured SessionMetricsResult.
func ParseSessionMetrics(toolResult *McpToolResult) *SessionMetricsResult {
	if toolResult == nil {
		return &SessionMetricsResult{
			Success:      false,
			Metrics:      nil,
			Raw:          nil,
			ErrorMessage: "get_metrics tool result is nil",
		}
	}

	if !toolResult.Success {
		return &SessionMetricsResult{
			ApiResponse:   WithRequestID(toolResult.RequestID),
			Success:       false,
			Metrics:       nil,
			Raw:           nil,
			ErrorMessage:  toolResult.ErrorMessage,
		}
	}

	var raw map[string]interface{}
	if err := json.Unmarshal([]byte(toolResult.Data), &raw); err != nil {
		return &SessionMetricsResult{
			ApiResponse:  WithRequestID(toolResult.RequestID),
			Success:      false,
			Metrics:      nil,
			Raw:          nil,
			ErrorMessage: fmt.Sprintf("Failed to parse get_metrics response: %v", err),
		}
	}

	var metrics SessionMetrics
	if err := json.Unmarshal([]byte(toolResult.Data), &metrics); err != nil {
		return &SessionMetricsResult{
			ApiResponse:  WithRequestID(toolResult.RequestID),
			Success:      false,
			Metrics:      nil,
			Raw:          raw,
			ErrorMessage: fmt.Sprintf("Failed to parse get_metrics response: %v", err),
		}
	}

	return &SessionMetricsResult{
		ApiResponse: WithRequestID(toolResult.RequestID),
		Success:     true,
		Metrics:     &metrics,
		Raw:         raw,
	}
}


