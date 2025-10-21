//go:build linux
// +build linux

package terminal

import (
	"syscall"
	"unsafe"
)

// IsTerminal checks if the output is going to a terminal (Linux version)
func IsTerminal(fd uintptr) bool {
	var termios syscall.Termios
	_, _, err := syscall.Syscall(syscall.SYS_IOCTL, fd, syscall.TCGETS, uintptr(unsafe.Pointer(&termios)))
	return err == 0
}
