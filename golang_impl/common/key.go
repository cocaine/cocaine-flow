package common

import (
	"fmt"
	"os"

	"io/ioutil"
)

func readKey(path string) (key []byte, err error) {
	fi, err := os.Stat(path)
	if err != nil {
		if os.IsNotExist(err) {
			err = fmt.Errorf("File: %s %s", path, err)
		}
		return
	}

	// -rw?------
	if fi.Mode().Perm()&0077 != 0 {
		err = fmt.Errorf("KeyFile permissions mode isn't secure %b", fi.Mode().Perm())
		return
	}

	key, err = ioutil.ReadFile(path)
	return
}
