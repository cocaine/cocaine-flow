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
}

type AuthCocaine interface {
	AuthController
}

type authCocaine struct {
	app     appWrapper
	tokener Tokenhandler
}

type authBackend struct {
	name string
	cocainebackend
}

/*

*/

func (ac *authCocaine) getBackend(ui UserInfo) (c Cocaine) {
	return &authBackend{
		ui.Name,
		cocainebackend{ac.app},
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

func NewBackend() (ac AuthCocaine, err error) {
	app, err := NewAppWrapper("flow-tools")
	if err != nil {
		return
	}

	ciph, err := aes.NewCipher(common.GetsScretKey())
	if err != nil {
		log.Printf("Error %s", err)
		return
	}

	ac = &authCocaine{
		app:     app,
		tokener: &Token{ciph},
	}
	return
}
