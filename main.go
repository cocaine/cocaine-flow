package main

import (
	"flag"
	"net/http"

	"github.com/cocaine/cocaine-flow/frontHTTP"
)

func main() {
	flag.Parse()
	h := frontHTTP.ConstructHandler()
	http.ListenAndServe(":8080", h)
}
