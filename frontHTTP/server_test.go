package frontHTTP

import (
	_ "bytes"
	"io"
	"net/http"
	"net/http/httptest"
	"net/url"
	"testing"
)

const testUser = "noxiouz"
const testUserPasswd = "qwerty"

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
	uv := url.Values{}
	uv.Set("name", testUser)
	uv.Set("password", testUserPasswd)

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

	AssertStatus("POST", ts.URL+"/flow/v1/groups/TEST/APP?weight=1", 200, nil, t)
	AssertStatus("DELETE", ts.URL+"/flow/v1/groups/TEST/APP", 200, nil, t)
	AssertStatus("DELETE", ts.URL+"/flow/v1/groups/TEST", 200, nil, t)
	AssertStatus("POST", ts.URL+"/flow/v1/groupsrefresh/", 200, nil, t)

	if r, err := http.PostForm(ts.URL+"/flow/v1/users/signup", uv); err != nil || r.StatusCode != 200 {
		t.Fatal(r, err)
	}

	if r, err := http.PostForm(ts.URL+"/flow/v1/users/signin", uv); err != nil || r.StatusCode != 200 {
		t.Fatal(r, err)
	}

	if r, err := http.PostForm(ts.URL+"/flow/v1/users/token", uv); err != nil || r.StatusCode != 200 {
		t.Fatal(r, err)
	}
}
