package backend

import (
	"flag"
)

var (
	CocaineEndpoint  string
	RegistryEndpoint string
	DockerEndpoint   string
)

func init() {
	const (
		defaultCocaine  = "localhost:10053"
		defaultDocker   = "unix://var/run/docker.sock"
		defaultRegistry = "localhost:5000"
	)

	flag.StringVar(&CocaineEndpoint, "cocaine", defaultCocaine, "cocaine endpoint")
	flag.StringVar(&DockerEndpoint, "docker", defaultDocker, "Docker endpoint")
	flag.StringVar(&RegistryEndpoint, "registry", defaultRegistry, "cocaine endpoint")
}
