package backend

import (
	"github.com/cocaine/cocaine-flow/common"
)

const null_arg = 0

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

type GroupController interface {
	GroupList() ([]string, error)
	GroupView(name string) (map[string]interface{}, error)
	GroupCreate(name string) error
	GroupRemove(name string) error

	GroupPushApp(name string, app string, weight int) error
	GroupPopApp(name string, app string) error
	GroupRefresh(name ...string) error
}

type CrashlogController interface {
	CrashlogList(name string) ([]string, error)
	CrashlogView(name string, timestamp int) (string, error)
}

type ApplicationController interface {
	// ApplicationList(username string) ([]string, error)
	ApplicationUpload(username string, appname string, path string) (chan string, *bool, error)
}

type UploadLogController interface {
	UploadLogList(username string) ([]string, error)
	UploadLogRead(id string) ([]byte, error)
}

type Cocaine interface {
	CrashlogController
	GroupController
	HostController
	ProfileController
	RunlistController
	ApplicationController
}

type cocainebackend struct {
	app appWrapper
	common.Context
}

/*
	ProfileController implementation
*/

func (b *cocainebackend) ProfileList() (list []string, err error) {
	err = b.app.Call("profile-list", null_arg, &list)
	return
}

func (b *cocainebackend) ProfileRead(name string) (pf map[string]interface{}, err error) {
	err = b.app.Call("profile-read", name, &pf)
	return
}

/*
	HostController impl
*/

func (b *cocainebackend) HostAdd(name string) (err error) {
	err = b.app.Call("host-add", name)
	return
}

func (b *cocainebackend) HostList() (hosts []string, err error) {
	err = b.app.Call("host-list", null_arg, &hosts)
	return
}

func (b *cocainebackend) HostRemove(name string) (err error) {
	err = b.app.Call("host-remove", name)
	return
}

/*
	RunlistController impl
*/

func (b *cocainebackend) RunlistList() (list []string, err error) {
	err = b.app.Call("runlist-list", null_arg, &list)
	return
}

func (b *cocainebackend) RunlistRead(name string) (runlist map[string]string, err error) {
	err = b.app.Call("runlist-read", name, &runlist)
	return
}

/*
	GroupController impl
*/

func (b *cocainebackend) GroupList() (list []string, err error) {
	err = b.app.Call("group-list", null_arg, &list)
	return
}

func (b *cocainebackend) GroupCreate(name string) (err error) {
	err = b.app.Call("group-create", name)
	return
}

func (b *cocainebackend) GroupRemove(name string) (err error) {
	err = b.app.Call("group-remove", name)
	return
}

func (b *cocainebackend) GroupView(name string) (gr map[string]interface{}, err error) {
	err = b.app.Call("group-read", name, &gr)
	return
}

func (b *cocainebackend) GroupPushApp(name string, app string, weight int) (err error) {
	task := map[string]interface{}{
		"name":   name,
		"app":    app,
		"weight": weight,
	}
	err = b.app.Call("group-pushapp", task)
	return
}

func (b *cocainebackend) GroupPopApp(name string, app string) (err error) {
	task := map[string]interface{}{
		"name": name,
		"app":  app,
	}
	err = b.app.Call("group-popapp", task)
	return
}

func (b *cocainebackend) GroupRefresh(name ...string) (err error) {
	var groupname string
	if len(name) == 1 {
		groupname = name[0]
	}
	err = b.app.Call("group-refresh", groupname)
	return
}

/*
	Crashlog impl
*/

func (b *cocainebackend) CrashlogList(name string) (crashlogs []string, err error) {
	err = b.app.Call("crashlog-list", name, &crashlogs)
	return
}

func (b *cocainebackend) CrashlogView(name string, timestamp int) (crashlog string, err error) {
	task := map[string]interface{}{
		"name":      name,
		"timestamp": timestamp,
	}
	err = b.app.Call("crashlog-view", task, &crashlog)
	return
}

/*
	ApplicationController impl
*/

//TBD - drop *bool
func (b *cocainebackend) ApplicationUpload(username string, appname string, path string) (ans chan string, isOk *bool, err error) {
	task := map[string]interface{}{
		"user":     username,
		"app":      appname,
		"path":     path,
		"docker":   b.Context.DockerEndpoint(),
		"registry": b.Context.RegistryEndpoint(),
	}
	stream, err := b.app.StreamCall("user-upload", task)
	if err != nil {
		return
	}

	isOk = new(bool)

	ans = make(chan string, 10)
	go func() {
		for {
			var logdata string
			select {
			case res, ok := <-stream:
				if !ok {
					close(ans)
					*isOk = true
					return
				}

				if res.Err() != nil {
					*isOk = false
					close(ans)
					return
				}

				extracterr := res.Extract(&logdata)
				if extracterr != nil {
					continue
				}

				if len(logdata) > 0 {
					ans <- logdata
				}
			}
		}
	}()
	//TBD TEMP
	return
}
