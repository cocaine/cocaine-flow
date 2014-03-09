package main

import (
	"log"
	"net/http"

	"github.com/cocaine/cocaine-flow/common"
	"github.com/cocaine/cocaine-flow/frontHTTP"
)

const testDocker = "http://192.168.57.100:3138"
const testCocaine = ":10053"
const testRegistry = "192.168.57.100:5000"

func main() {
	cfg := common.ContextCfg{
		Docker:   testDocker,
		Registry: testRegistry,
		Cocaine:  testCocaine,
		KeyFile:  "/Users/noxiouz/Gotest/src/github.com/cocaine/cocaine-flow/test/keyfile.cfg",
	}
	err := common.InitializeContext(cfg)
	if err != nil {
		log.Fatalln(err)
	}
	h := frontHTTP.ConstructHandler()
	http.ListenAndServe(":8080", h)
}
