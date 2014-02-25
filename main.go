package main

import (
	"net/http"

	"github.com/cocaine/cocaine-flow/frontHTTP"
)

func main() {
	h := frontHTTP.ConstructHandler()
	http.ListenAndServe(":8080", h)
}
