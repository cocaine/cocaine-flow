package archive

import (
	"io"
	"io/ioutil"
	"os"
	"os/exec"
)

const prefix = "flow"

type Archive io.Reader

// I hope I'll rewrite this =)

func Unpack(archive Archive) (path string, err error) {
	path, err = ioutil.TempDir("", prefix)
	if err != nil {
		return
	}

	f, err := ioutil.TempFile(path, prefix)
	defer f.Close()
	defer os.Remove(f.Name())

	body, err := ioutil.ReadAll(archive)
	if err != nil {
		return
	}

	_, err = f.Write(body)
	if err != nil {
		return
	}
	cmd := exec.Command("tar", "-C", path, "-xvf", f.Name())
	err = cmd.Run()
	if err != nil {
		return
	}
	return
}
