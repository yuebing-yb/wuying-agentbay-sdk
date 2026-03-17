package internal

// Logger defines the interface for SDK logging. Sub-packages (browser, mobile, filesystem)
// use type assertion on the session to obtain a Logger when available.
// The agentbay.Session implements this interface.
type Logger interface {
	LogDebug(msg string)
	LogInfo(msg string)
	LogWarn(msg string)
	LogError(msg string)
}
