package models

import (
	"encoding/json"
	"fmt"
)

func getInt64FromMap(raw map[string]interface{}, key string) int64 {
	v, ok := raw[key]
	if !ok || v == nil {
		return 0
	}
	switch t := v.(type) {
	case float64:
		return int64(t)
	case int64:
		return t
	case int:
		return int64(t)
	case json.Number:
		i, _ := t.Int64()
		return i
	default:
		return 0
	}
}

func getIntFromMap(raw map[string]interface{}, key string) int {
	return int(getInt64FromMap(raw, key))
}

func getFloat64FromMap(raw map[string]interface{}, key string) float64 {
	v, ok := raw[key]
	if !ok || v == nil {
		return 0
	}
	switch t := v.(type) {
	case float64:
		return t
	case float32:
		return float64(t)
	case int:
		return float64(t)
	case int64:
		return float64(t)
	case json.Number:
		f, _ := t.Float64()
		return f
	default:
		return 0
	}
}

func getStringFromMap(raw map[string]interface{}, key string) string {
	v, ok := raw[key]
	if !ok || v == nil {
		return ""
	}
	switch t := v.(type) {
	case string:
		return t
	default:
		return fmt.Sprintf("%v", v)
	}
}

func getFloat64FromFirstKey(raw map[string]interface{}, keys []string) float64 {
	for _, k := range keys {
		if _, ok := raw[k]; ok {
			return getFloat64FromMap(raw, k)
		}
	}
	return 0
}

// SessionMetrics represents structured runtime metrics for session monitoring.
type SessionMetrics struct {
	CpuCount   int     `json:"cpu_count"`
	CpuUsedPct float64 `json:"cpu_used_pct"`

	DiskTotal int64 `json:"disk_total"`
	DiskUsed  int64 `json:"disk_used"`

	MemTotal int64 `json:"mem_total"`
	MemUsed  int64 `json:"mem_used"`

	RxRateKbytePerS float64 `json:"rx_rate_kbyte_per_s"`
	TxRateKbytePerS float64 `json:"tx_rate_kbyte_per_s"`
	RxUsedKbyte     float64 `json:"rx_used_kbyte"`
	TxUsedKbyte     float64 `json:"tx_used_kbyte"`

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

func parseSessionMetricsFromRaw(raw map[string]interface{}) *SessionMetrics {
	if raw == nil {
		return nil
	}
	return &SessionMetrics{
		CpuCount:   getIntFromMap(raw, "cpu_count"),
		CpuUsedPct: getFloat64FromMap(raw, "cpu_used_pct"),
		DiskTotal:  getInt64FromMap(raw, "disk_total"),
		DiskUsed:   getInt64FromMap(raw, "disk_used"),
		MemTotal:   getInt64FromMap(raw, "mem_total"),
		MemUsed:    getInt64FromMap(raw, "mem_used"),
		RxRateKbytePerS: getFloat64FromFirstKey(
			raw,
			[]string{"rx_rate_kbyte_per_s", "rx_rate_kbps", "rx_rate_KBps"},
		),
		TxRateKbytePerS: getFloat64FromFirstKey(
			raw,
			[]string{"tx_rate_kbyte_per_s", "tx_rate_kbps", "tx_rate_KBps"},
		),
		RxUsedKbyte: getFloat64FromFirstKey(raw, []string{"rx_used_kbyte", "rx_used_kb", "rx_used_KB"}),
		TxUsedKbyte: getFloat64FromFirstKey(raw, []string{"tx_used_kbyte", "tx_used_kb", "tx_used_KB"}),
		Timestamp:   getStringFromMap(raw, "timestamp"),
	}
}

// ParseSessionMetrics parses the metrics response into a structured SessionMetricsResult.
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

	metrics := parseSessionMetricsFromRaw(raw)

	return &SessionMetricsResult{
		ApiResponse: WithRequestID(toolResult.RequestID),
		Success:     true,
		Metrics:     metrics,
		Raw:         raw,
	}
}


