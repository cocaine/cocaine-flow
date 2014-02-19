package main

import (
	"log"

	"github.com/ugorji/go/codec"

	"github.com/cocaine/cocaine-framework-go/cocaine"
)

const null_arg = 0

var (
	mh codec.MsgpackHandle
	h  = &mh
)

/*
	Application helper
*/

type appWrapper struct {
	app *cocaine.Service
}

func (aW *appWrapper) Call(method string, args interface{}, result ...interface{}) (err error) {
	var buf []byte
	err = codec.NewEncoderBytes(&buf, h).Encode(args)
	if err != nil {
		return
	}

	res, isOpen := <-aW.app.Call("enqueue", method, buf)
	if !isOpen {
		return nil
	}

	err = res.Err()
	if err != nil {
		return
	}

	if len(result) == 1 {
		err = res.Extract(result[0])
	}
	return
}

/*
	Content interfaces
*/

type ProfileController interface {
	ProfileList() ([]string, error)
	ProfileRead(name string) (map[string]interface{}, error)
}

type HostController interface {
	HostAdd(name string) error
	HostRemove(name string) error
	HostList() ([]string, error)
}

type RunlistController interface {
	RunlistRead(name string) (map[string]string, error)
	RunlistList() ([]string, error)
}

type Cocaine interface {
	HostController
	ProfileController
	RunlistController
}

type backend struct {
	app appWrapper
}

/*
	ProfileController implementation
*/

func (b *backend) ProfileList() (list []string, err error) {
	err = b.app.Call("profile-list", null_arg, &list)
	return
}

func (b *backend) ProfileRead(name string) (pf map[string]interface{}, err error) {
	err = b.app.Call("profile-read", name, &pf)
	return
}

/*
	HostController impl
*/

func (b *backend) HostAdd(name string) (err error) {
	err = b.app.Call("host-add", name)
	return
}

func (b *backend) HostList() (hosts []string, err error) {
	err = b.app.Call("host-list", null_arg, &hosts)
	return
}

func (b *backend) HostRemove(name string) (err error) {
	err = b.app.Call("host-remove", name)
	return
}

/*
	RunlistController impl
*/

func (b *backend) RunlistList() (list []string, err error) {
	err = b.app.Call("runlist-list", null_arg, &list)
	return
}

func (b *backend) RunlistRead(name string) (runlist map[string]string, err error) {
	err = b.app.Call("runlist-read", name, &runlist)
	return
}

/*
	New
*/

func NewBackend() (c Cocaine, err error) {
	app, err := cocaine.NewService("flow-tools")
	if err != nil {
		log.Printf("Error %s", err)
		return
	}

	c = &backend{
		app: appWrapper{app: app},
	}
	return
}
