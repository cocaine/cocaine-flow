package common

import (
	"fmt"
	"sync"
)

type ContextCfg struct {
	Docker   string
	Registry string
	Cocaine  string
}

type Context interface {
	DockerEndpoint() string
	RegistryEndpoint() string
	CocaineEndpoint() string
}

var (
	_contextMutex  sync.Mutex
	_globalContext Context = nil
)

type context struct {
	docker   string
	registry string
	cocaine  string
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

func GetContext() (c Context, err error) {
	_contextMutex.Lock()
	defer _contextMutex.Unlock()
	if _globalContext == nil {
		err = fmt.Errorf("Context isn't initialized")
		return
	}

	return _globalContext, nil
}

func InitializeContext(cfg ContextCfg) error {
	_contextMutex.Lock()
	defer _contextMutex.Unlock()
	if _globalContext != nil {
		return fmt.Errorf("Context has been already initialized")
	}

	_globalContext = &context{
		docker:   cfg.Docker,
		registry: cfg.Registry,
		cocaine:  cfg.Cocaine,
	}
	return nil
}
