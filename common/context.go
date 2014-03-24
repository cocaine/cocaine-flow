package common

import (
	"fmt"
	"strings"
	"sync"
)

type ContextCfg struct {
	Docker   string
	Registry string
	Cocaine  string
	KeyFile  string
}

type Context interface {
	DockerEndpoint() string
	RegistryEndpoint() string
	CocaineEndpoint() string
	SecretKey() []byte
}

var (
	_contextMutex  sync.Mutex
	_globalContext Context = nil
)

type context struct {
	docker    string
	registry  string
	cocaine   string
	secretkey []byte
}

func (c *context) DockerEndpoint() string {
	return c.docker
}

func (c *context) RegistryEndpoint() string {
	return c.registry
}

func (c *context) CocaineEndpoint() string {
	return c.cocaine
}

func (c *context) SecretKey() []byte {
	return c.secretkey
}

func GetContext() (c Context, err error) {
	_contextMutex.Lock()
	defer _contextMutex.Unlock()
	if _globalContext == nil {
		err = fmt.Errorf("Context isn't initialized")
		return
	}

	return _globalContext, nil
}

func InitializeContext(cfg ContextCfg) (err error) {
	_contextMutex.Lock()
	defer _contextMutex.Unlock()
	if _globalContext != nil {
		return fmt.Errorf("Context has been already initialized")
	}

	if len(strings.Trim(cfg.KeyFile, " ")) == 0 {
		err = fmt.Errorf("Empty KeyFile path")
		return
	}

	key, err := readKey(cfg.KeyFile)
	if err != nil {
		return
	}

	_globalContext = &context{
		docker:    cfg.Docker,
		registry:  cfg.Registry,
		cocaine:   cfg.Cocaine,
		secretkey: key,
	}
	return nil
}
