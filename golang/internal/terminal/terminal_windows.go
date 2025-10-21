//go:build windows
// +build windows

package terminal

import (
	"syscall"
	"unsafe"
)

var (
	kernel32           = syscall.NewLazyDLL("kernel32.dll")
	procGetConsoleMode = kernel32.NewProc("GetConsoleMode")
)

// IsTerminal checks if the output is going to a terminal (Windows version)
func IsTerminal(fd uintptr) bool {
	var mode uint32
	r, _, _ := procGetConsoleMode.Call(fd, uintptr(unsafe.Pointer(&mode)))
	return r != 0
}
