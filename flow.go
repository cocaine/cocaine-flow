package main

import (
	"crypto/aes"
	"crypto/cipher"
	"crypto/rand"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"log"
	"time"

	"github.com/ugorji/go/codec"

	"github.com/cocaine/cocaine-framework-go/cocaine"
)

const null_arg = 0
const token_lifetime = 3600 // sec

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

type Tokenhandler interface {
	Encrypt(*UserInfo) (string, error)
	Decrypt(string) (UserInfo, error)
}

type Token struct {
	block cipher.Block
}

type tokenWrapper struct {
	UI       *UserInfo
	Lifetime int64
}

func (t *Token) Encrypt(ui *UserInfo) (tok string, err error) {
	elapsedTime := time.Now().Add(time.Second * token_lifetime).Unix()
	value, err := json.Marshal(tokenWrapper{ui, elapsedTime})
	if err != nil {
		return
	}

	iv := make([]byte, t.block.BlockSize())
	rand.Read(iv)

	stream := cipher.NewCTR(t.block, iv)
	stream.XORKeyStream(value, value)
	tok = hex.EncodeToString(append(iv, value...))
	return
}

func (t *Token) Decrypt(tok string) (ui UserInfo, err error) {

	value, err := hex.DecodeString(tok)
	if err != nil {
		err = fmt.Errorf("Corrupted token")
		return
	}

	if len(value) < t.block.BlockSize() {
		err = fmt.Errorf("Too short to be decrypted, %d", len(value))
		return
	}

	iv := value[:t.block.BlockSize()]
	value = value[t.block.BlockSize():]
	stream := cipher.NewCTR(t.block, iv)
	stream.XORKeyStream(value, value)

	var wui tokenWrapper
	err = json.Unmarshal(value, &wui)
	if err != nil {
		return
	}

	elapsedTime := time.Unix(wui.Lifetime, 0)
	if time.Now().After(elapsedTime) {
		err = fmt.Errorf("Token has expired")
		return
	}

	ui = *wui.UI
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

type GroupController interface {
	GroupList() ([]string, error)
	GroupView(name string) (map[string]interface{}, error)
	GroupCreate(name string) error
	GroupRemove(name string) error

	GroupPushApp(name string, app string, weight int) error
	GroupPopApp(name string, app string) error
	GroupRefresh(name ...string) error
}

type AuthController interface {
	UserSignin(name, password string) (UserInfo, error)
	UserSignup(name, password string) error
	UserRemove(name string) error
	GenToken(name, password string) (string, error)
	ValidateToken(token string) (UserInfo, error)
}

type CrashlogController interface {
	CrashlogList(name string) ([]string, error)
	CrashlogView(name string, timestamp int) (string, error)
}

type UserInfo struct {
	Name string `codec:"name"`
}

type Cocaine interface {
	CrashlogController
	GroupController
	HostController
	ProfileController
	RunlistController
	AuthController
}

type backend struct {
	app     appWrapper
	tokener Tokenhandler
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
	GroupController impl
*/

func (b *backend) GroupList() (list []string, err error) {
	err = b.app.Call("group-list", null_arg, &list)
	return
}

func (b *backend) GroupCreate(name string) (err error) {
	err = b.app.Call("group-create", name)
	return
}

func (b *backend) GroupRemove(name string) (err error) {
	err = b.app.Call("group-remove", name)
	return
}

func (b *backend) GroupView(name string) (gr map[string]interface{}, err error) {
	err = b.app.Call("group-read", name, &gr)
	return
}

func (b *backend) GroupPushApp(name string, app string, weight int) (err error) {
	task := map[string]interface{}{
		"name":   name,
		"app":    app,
		"weight": weight,
	}
	err = b.app.Call("group-pushapp", task)
	return
}

func (b *backend) GroupPopApp(name string, app string) (err error) {
	task := map[string]interface{}{
		"name": name,
		"app":  app,
	}
	err = b.app.Call("group-popapp", task)
	return
}

func (b *backend) GroupRefresh(name ...string) (err error) {
	var groupname string
	if len(name) == 1 {
		groupname = name[0]
	}
	err = b.app.Call("group-refresh", groupname)
	return
}

/*
	AuthController impl
*/

func (b *backend) UserSignin(name, password string) (ui UserInfo, err error) {
	task := map[string]string{
		"name":     name,
		"password": password,
	}
	err = b.app.Call("user-signin", task, &ui)
	return
}

func (b *backend) UserSignup(name, password string) (err error) {
	task := map[string]string{
		"name":     name,
		"password": password,
	}
	err = b.app.Call("user-signup", task)
	return
}

func (b *backend) UserRemove(name string) (err error) {
	err = b.app.Call("user-remove", name)
	return
}

func (b *backend) GenToken(name, password string) (token string, err error) {
	ui, err := b.UserSignin(name, password)
	if err != nil {
		return
	}
	token, err = b.tokener.Encrypt(&ui)
	return
}

func (b *backend) ValidateToken(token string) (ui UserInfo, err error) {
	ui, err = b.tokener.Decrypt(token)
	return
}

/*
	Crashlog impl
*/

func (b *backend) CrashlogList(name string) (crashlogs []string, err error) {
	err = b.app.Call("crashlog-list", name, &crashlogs)
	return
}

func (b *backend) CrashlogView(name string, timestamp int) (crashlog string, err error) {
	task := map[string]interface{}{
		"name":      name,
		"timestamp": timestamp,
	}
	err = b.app.Call("crashlog-view", task, &crashlog)
	return
}

func NewBackend() (c Cocaine, err error) {
	app, err := cocaine.NewService("flow-tools")
	if err != nil {
		log.Printf("Error %s", err)
		return
	}

	ciph, err := aes.NewCipher(secretkey)
	if err != nil {
		log.Printf("Error %s", err)
		return
	}

	c = &backend{
		app:     appWrapper{app: app},
		tokener: &Token{ciph},
	}
	return
}
