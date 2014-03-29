package main

import (
	"flag"
	"log"
	"net/http"

	"github.com/cocaine/cocaine-flow/common"
	"github.com/cocaine/cocaine-flow/frontHTTP"
)

func main() {
	dockerEndpoint := flag.String("docker", "unix:///var/run/docker.sock", "dockersocket unix:// or http://")
	cocaineEndpoint := flag.String("cocaine", ":10053", "cocaine-runtime")
	registryEndpoint := flag.String("registry", ":5000", "registry endpoint")
	keyFile := flag.String("keyfile", "", "keyfile path")
	serverEndpoint := flag.String("-H", ":8080", "")
	flag.Parse()

	cfg := common.ContextCfg{
		Docker:   *dockerEndpoint,
		Registry: *registryEndpoint,
		Cocaine:  *cocaineEndpoint,
		KeyFile:  *keyFile,
	}
	err := common.InitializeContext(cfg)
	if err != nil {
		log.Fatalln(err)
	}
	h := frontHTTP.ConstructHandler()
	http.ListenAndServe(*serverEndpoint, h)
}
