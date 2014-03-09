package backend

import (
	"crypto/aes"
	"log"

	"github.com/cocaine/cocaine-flow/common"
)

type AuthController interface {
	UserSignin(name, password string) (Cocaine, error)
	UserSignup(name, password string) error
	UserRemove(name string) error
	GenToken(name, password string) (string, error)
	ValidateToken(token string) (Cocaine, error)
	GuestAccount() (Cocaine, error)
}

type UserInfo struct {
	Name string `codec:"name"`
}

type AuthCocaine interface {
	AuthController
}

type authCocaine struct {
	app     appWrapper
	tokener Tokenhandler
	context common.Context
}

type authBackend struct {
	name string
	cocainebackend
}

/*
	ApplicationController
*/

func (a *authBackend) ApplicationUpload(info AppUplodaInfo) (<-chan string, <-chan error, error) {
	return a.cocainebackend.ApplicationUpload(a.name, info)
}

func (a *authBackend) ApplicationList() ([]string, error) {
	/*
		Insert ACL hook for admin in future
	*/
	return a.cocainebackend.ApplicationList(a.name)
}

/*
	BuildlogContorller
*/

func (a *authBackend) BuildLogList() ([]string, error) {
	return a.cocainebackend.BuildLogList(a.name)
}

/*

*/

func (ac *authCocaine) getBackend(ui UserInfo) (c Cocaine) {
	return &authBackend{
		ui.Name,
		cocainebackend{ac.app, ac.context},
	}
}

func (ac *authCocaine) signin(name, password string) (ui UserInfo, err error) {
	task := map[string]string{
		"name":     name,
		"password": password,
	}
	err = ac.app.Call("user-signin", task, &ui)
	return
}

/*
	AuthController impl
*/

func (ac *authCocaine) UserSignin(name, password string) (c Cocaine, err error) {
	ui, err := ac.signin(name, password)
	if err != nil {
		return
	}
	c = ac.getBackend(ui)
	return
}

func (ac *authCocaine) UserSignup(name, password string) (err error) {
	task := map[string]string{
		"name":     name,
		"password": password,
	}
	err = ac.app.Call("user-signup", task)
	return
}

func (ac *authCocaine) UserRemove(name string) (err error) {
	err = ac.app.Call("user-remove", name)
	return
}

func (ac *authCocaine) GenToken(name, password string) (token string, err error) {
	ui, err := ac.signin(name, password)
	if err != nil {
		return
	}
	token, err = ac.tokener.Encrypt(&ui)
	return
}

func (ac *authCocaine) ValidateToken(token string) (c Cocaine, err error) {
	ui, err := ac.tokener.Decrypt(token)
	if err != nil {
		return
	}

	c = ac.getBackend(ui)
	return
}

// Temp
func (ac *authCocaine) GuestAccount() (c Cocaine, err error) {
	c = &authBackend{
		"GUEST",
		cocainebackend{ac.app, ac.context},
	}
	return
}

func NewBackend() (ac AuthCocaine, err error) {
	context, err := common.GetContext()
	if err != nil {
		return
	}

	app, err := NewAppWrapper("flow-tools")
	if err != nil {
		return
	}

	ciph, err := aes.NewCipher(context.SecretKey())
	if err != nil {
		log.Printf("Error %s", err)
		return
	}

	ac = &authCocaine{
		app:     app,
		tokener: &Token{ciph},
		context: context,
	}
	return
}
