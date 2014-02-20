package main

import (
	"io"
	"net/http"
	"net/http/httptest"
	"testing"
)

func AssertStatus(method string, urlStr string, status int, body io.Reader, t *testing.T) {
	cl := http.Client{}
	req, _ := (http.NewRequest(method, urlStr, body))
	r, err := cl.Do(req)
	if err != nil {
		t.Fatal(err)
	}
	if r.StatusCode != status {
		t.Fatalf("%s Unexpected status %s %s", method, urlStr, r.Status)
	}
}

func TestServer(t *testing.T) {
	ts := httptest.NewServer(ConstructHandler())
	defer ts.Close()
	t.Logf("Test server is runing on %s", ts.URL)

	AssertStatus("GET", ts.URL+"/ping", 200, nil, t)
	AssertStatus("GET", ts.URL+"/flow/v1/hosts/", 200, nil, t)
	AssertStatus("POST", ts.URL+"/flow/v1/hosts/HOST2", 200, nil, t)
	AssertStatus("DELETE", ts.URL+"/flow/v1/hosts/HOST3", 200, nil, t)

	AssertStatus("GET", ts.URL+"/flow/v1/profiles/", 200, nil, t)
	AssertStatus("GET", ts.URL+"/flow/v1/profiles/TEST", 200, nil, t)

	AssertStatus("GET", ts.URL+"/flow/v1/runlists/", 200, nil, t)
	AssertStatus("GET", ts.URL+"/flow/v1/runlists/default", 200, nil, t)

	AssertStatus("GET", ts.URL+"/flow/v1/groups/", 200, nil, t)
	AssertStatus("POST", ts.URL+"/flow/v1/groups/TEST", 200, nil, t)
	AssertStatus("GET", ts.URL+"/flow/v1/groups/TEST", 200, nil, t)

	AssertStatus("POST", ts.URL+"/flow/v1/groups/TEST/APP", 200, nil, t)
	AssertStatus("DELETE", ts.URL+"/flow/v1/groups/TEST/APP", 200, nil, t)
	AssertStatus("DELETE", ts.URL+"/flow/v1/groups/TEST", 200, nil, t)
	AssertStatus("POST", ts.URL+"/flow/v1/groupsrefresh/", 200, nil, t)
}
