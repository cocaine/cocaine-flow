package frontHTTP

import (
	"bytes"
	"encoding/json"
	"io"
	"io/ioutil"
	"net/http"
	"net/http/httptest"
	"net/url"
	"testing"

	"github.com/cocaine/cocaine-flow/common"
)

const testUser = "noxiouz"
const testUserPasswd = "qwerty"
const testDocker = "http://192.168.57.100:3138"
const testCocaine = ":10053"
const testRegistry = "192.168.57.100:5000"
const testPackage = "/Users/noxiouz/Gotest/src/github.com/cocaine/cocaine-flow/test/testapp/TEST.tar.gz"

func AssertStatus(method string, urlStr string, status int, body io.Reader, t *testing.T) (rbody []byte) {
	cl := http.Client{}
	req, _ := (http.NewRequest(method, urlStr, body))
	r, err := cl.Do(req)
	if err != nil {
		t.Fatal(err)
	}
	defer r.Body.Close()
	rbody, err = ioutil.ReadAll(r.Body)
	if r.StatusCode != status {
		if err != nil {
			t.Fatal(err)
		}
		t.Fatalf("%s Unexpected status %s %s %s", method, urlStr, r.Status, string(rbody))
	}
	return
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

func TestInit(t *testing.T) {
	cfg := common.ContextCfg{
		Docker:   testDocker,
		Registry: testRegistry,
		Cocaine:  testCocaine,
		KeyFile:  "/Users/noxiouz/Gotest/src/github.com/cocaine/cocaine-flow/test/keyfile.cfg",
	}
	err := common.InitializeContext(cfg)
	if err != nil {
		t.Fatalf("Context initialization error %s", err)
	}

	_, err = common.GetContext()
	if err != nil {
		t.Fatalf("GetContext error %s", err)
	}
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
	testProfile := map[string]interface{}{
		"pool-limit": 99999999,
	}

	body, err := json.Marshal(testProfile)
	if err != nil {
		t.Logf("Bad json %s", err)
	}
	ts := httptest.NewServer(ConstructHandler())
	defer ts.Close()
	token := getToken(ts, t)
	AssertStatus("POST", ts.URL+"/flow/v1/profiles/NOXIOUZTESTPROFILE"+"?token="+token, 500, bytes.NewBuffer(body[:2]), t)
	AssertStatus("POST", ts.URL+"/flow/v1/profiles/NOXIOUZTESTPROFILE"+"?token="+token, 500, nil, t)
	AssertStatus("POST", ts.URL+"/flow/v1/profiles/NOXIOUZTESTPROFILE"+"?token="+token, 200, bytes.NewBuffer(body), t)
	AssertStatus("GET", ts.URL+"/flow/v1/profiles/"+"?token="+token, 200, nil, t)
	AssertStatus("GET", ts.URL+"/flow/v1/profiles/NOXIOUZTESTPROFILE"+"?token="+token, 200, nil, t)
	AssertStatus("DELETE", ts.URL+"/flow/v1/profiles/NOXIOUZTESTPROFILE"+"?token="+token, 200, nil, t)
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

	t.SkipNow()
	AssertStatus("POST", ts.URL+"/flow/v1/groupsrefresh/"+"?token="+token, 200, nil, t)
}

func TestCrashlogs(t *testing.T) {
	ts := httptest.NewServer(ConstructHandler())
	defer ts.Close()
	token := getToken(ts, t)
	AssertStatus("GET", ts.URL+"/flow/v1/crashlogs/flow-tools"+"?token="+token, 200, nil, t)
	// Add test for reading
}

func TestBuildLog(t *testing.T) {
	ts := httptest.NewServer(ConstructHandler())
	defer ts.Close()
	token := getToken(ts, t)

	AssertStatus("GET", ts.URL+"/flow/v1/buildlog/"+"?token="+token, 200, nil, t)
}

func TestApp(t *testing.T) {
	ts := httptest.NewServer(ConstructHandler())
	defer ts.Close()
	token := getToken(ts, t)

	body, err := ioutil.ReadFile(testPackage)
	if err != nil {
		t.Fatalf("Unable to perfom test %s", err)
	}
	b := AssertStatus("POST", ts.URL+"/flow/v1/app/bullet/first"+"?token="+token, 200, bytes.NewBuffer(body), t)
	t.Logf("%s", b)

	AssertStatus("POST", ts.URL+"/flow/v1/appstart"+"?name=bullet_first&profile=TEST&token="+token, 200, nil, t)
	AssertStatus("POST", ts.URL+"/flow/v1/appstop"+"?name=bullet_first&token="+token, 200, nil, t)
}
