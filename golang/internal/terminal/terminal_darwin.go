//go:build darwin || freebsd || netbsd || openbsd
// +build darwin freebsd netbsd openbsd

package terminal

import (
	"syscall"
	"unsafe"
)

// IsTerminal checks if the output is going to a terminal (BSD/Darwin version)
func IsTerminal(fd uintptr) bool {
	var termios syscall.Termios
	_, _, err := syscall.Syscall(syscall.SYS_IOCTL, fd, syscall.TIOCGETA, uintptr(unsafe.Pointer(&termios)))
	return err == 0
}
