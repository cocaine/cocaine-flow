package frontHTTP

import (
	_ "bytes"
	"io"
	"io/ioutil"
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
		defer r.Body.Close()
		body, err := ioutil.ReadAll(r.Body)
		if err != nil {
			t.Fatal(err)
		}
		t.Fatal(r.StatusCode, string(body))
		t.Fatalf("%s Unexpected status %s %s", method, urlStr, r.Status)
	}
}

func getToken(ts *httptest.Server, t *testing.T) (token string) {
	uv := url.Values{}
	uv.Set("name", testUser)
	uv.Set("password", testUserPasswd)

	resp, err := http.PostForm(ts.URL+"/flow/v1/users/token", uv)

	if err != nil || resp.StatusCode != 200 {
		t.Fatal(resp, err)
	}
	defer resp.Body.Close()
	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		t.Fatal(err)
	}
	token = string(body)
	return token
}

func BTestAuth(t *testing.T) {
	ts := httptest.NewServer(ConstructHandler())
	defer ts.Close()

	uv := url.Values{}
	uv.Set("name", testUser)
	uv.Set("password", testUserPasswd)

	r, err := http.PostForm(ts.URL+"/flow/v1/users/signup", uv)
	if err != nil {
		t.Fatal(err)
	}
	if r.StatusCode != 200 {
		defer r.Body.Close()
		body, err := ioutil.ReadAll(r.Body)
		if err != nil {
			t.Fatal(err)
		}
		t.Fatal(r.StatusCode, string(body))
	}

	r, err = http.PostForm(ts.URL+"/flow/v1/users/signin", uv)
	if err != nil {
		t.Fatal(err)
	}
	if r.StatusCode != 200 {
		defer r.Body.Close()
		body, err := ioutil.ReadAll(r.Body)
		if err != nil {
			t.Fatal(err)
		}
		t.Fatal(r.StatusCode, string(body))
	}
}

func TestHosts(t *testing.T) {
	ts := httptest.NewServer(ConstructHandler())
	defer ts.Close()
	token := getToken(ts, t)
	AssertStatus("GET", ts.URL+"/flow/v1/hosts/"+"?token="+token, 200, nil, t)
	AssertStatus("POST", ts.URL+"/flow/v1/hosts/HOST2"+"?token="+token, 200, nil, t)
	AssertStatus("DELETE", ts.URL+"/flow/v1/hosts/HOST3"+"?token="+token, 200, nil, t)
}

func TestProfiles(t *testing.T) {
	ts := httptest.NewServer(ConstructHandler())
	defer ts.Close()
	token := getToken(ts, t)
	AssertStatus("GET", ts.URL+"/flow/v1/profiles/"+"?token="+token, 200, nil, t)
	AssertStatus("GET", ts.URL+"/flow/v1/profiles/TEST"+"?token="+token, 200, nil, t)
}

func TestRunlists(t *testing.T) {
	ts := httptest.NewServer(ConstructHandler())
	defer ts.Close()
	token := getToken(ts, t)
	AssertStatus("GET", ts.URL+"/flow/v1/runlists/"+"?token="+token, 200, nil, t)
	AssertStatus("GET", ts.URL+"/flow/v1/runlists/default"+"?token="+token, 200, nil, t)
}

func TestGroups(t *testing.T) {
	ts := httptest.NewServer(ConstructHandler())
	defer ts.Close()
	token := getToken(ts, t)

	AssertStatus("GET", ts.URL+"/flow/v1/groups/"+"?token="+token, 200, nil, t)
	AssertStatus("POST", ts.URL+"/flow/v1/groups/TEST"+"?token="+token, 200, nil, t)
	AssertStatus("GET", ts.URL+"/flow/v1/groups/TEST"+"?token="+token, 200, nil, t)
	AssertStatus("POST", ts.URL+"/flow/v1/groupsrefresh/"+"?token="+token, 200, nil, t)
}
