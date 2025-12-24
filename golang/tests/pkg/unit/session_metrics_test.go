package agentbay_test

import (
	"testing"

	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay/models"
	"github.com/stretchr/testify/assert"
)

func TestParseSessionMetrics_Success(t *testing.T) {
	toolResult := &models.McpToolResult{
		Success:   true,
		RequestID: "req-1",
		Data:     `{"cpu_count":4,"cpu_used_pct":1.0,"disk_total":105286258688,"disk_used":30269431808,"mem_total":7918718976,"mem_used":2139729920,"rx_rate_KBps":0.22,"tx_rate_KBps":0.38,"rx_used_KB":1247.27,"tx_used_KB":120.13,"timestamp":"2025-12-24T10:54:23+08:00"}`,
	}

	result := models.ParseSessionMetrics(toolResult)
	assert.True(t, result.Success)
	assert.Equal(t, "req-1", result.RequestID)
	assert.NotNil(t, result.Metrics)
	assert.Equal(t, 4, result.Metrics.CpuCount)
	assert.InDelta(t, 1.0, result.Metrics.CpuUsedPct, 0.000001)
	assert.Equal(t, int64(7918718976), result.Metrics.MemTotal)
	assert.Equal(t, "2025-12-24T10:54:23+08:00", result.Metrics.Timestamp)
	assert.NotNil(t, result.Raw)
}

func TestParseSessionMetrics_InvalidJSON(t *testing.T) {
	toolResult := &models.McpToolResult{
		Success:   true,
		RequestID: "req-2",
		Data:     "{not-json}",
	}

	result := models.ParseSessionMetrics(toolResult)
	assert.False(t, result.Success)
	assert.Equal(t, "req-2", result.RequestID)
	assert.Nil(t, result.Metrics)
	assert.Contains(t, result.ErrorMessage, "Failed to parse get_metrics response")
}


