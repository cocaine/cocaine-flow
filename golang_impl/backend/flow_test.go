package backend

import (
	"encoding/json"
	"io/ioutil"
	"strconv"
	"strings"
	"testing"

	"github.com/cocaine/cocaine-flow/common"
)

const testUser = "noxiouz"
const testUserPasswd = "qwerty"
const testDocker = "http://192.168.57.100:3138"
const testCocaine = ":10053"
const testRegistry = "192.168.57.100:5000"

func createContext() {
	cfg := common.ContextCfg{
		Docker:   testDocker,
		Registry: testRegistry,
		Cocaine:  testCocaine,
		KeyFile:  "/Users/noxiouz/Gotest/src/github.com/cocaine/cocaine-flow/test/keyfile.cfg",
	}
	common.InitializeContext(cfg)
}

func getTestCocaine(t *testing.T) (c Cocaine) {

	b, err := NewBackend()
	if err != nil {
		t.Fatalf("Unable to create backend %s ", err)
	}

	c, err = b.UserSignin(testUser, testUserPasswd)
	if err != nil {
		t.Fatalf("Unable to auth %s ", err)
	}
	return
}

func TestAuth(t *testing.T) {
	// Create backend
	createContext()
	b, err := NewBackend()
	if err != nil {
		t.Fatalf("Unable to create backend %s ", err)
	}

	//Pretest cleaning
	_ = b.UserRemove(testUser)

	//Auth
	err = b.UserSignup(testUser, testUserPasswd)
	if err != nil {
		t.Fatal(err)
	}

	token, err := b.GenToken(testUser, testUserPasswd)
	if err != nil {
		t.Fatal(err)
	}

	_, err = b.GenToken(testUser, "CHAOS")
	if err == nil {
		t.Fatal("Error is expected. Got nil")
	}

	t.Logf("Token %s", token)

	_, err = b.ValidateToken(token)
	if err != nil {
		t.Fatal(err)
	}

	_, err = b.ValidateToken("CHAOS")
	if err == nil {
		t.Fatal(err)
	}

	_, err = b.UserSignin(testUser, testUserPasswd)
	if err != nil {
		t.Fatal(err)
	}

	_, err = b.UserSignin(testUser, "CHAOS")
	if err == nil {
		t.Fatal("Error is expected. Got nil")
	}

	_, err = b.GuestAccount()
	if err != nil {
		t.Fatal(err)
	}

}

func TestProfile(t *testing.T) {
	cocs := getTestCocaine(t)

	// List of profiles
	profiles, err := cocs.ProfileList()
	if err != nil {
		t.Fatalf("Unable to get list of profiles %s", err)
	}

	// Read every profile
	t.Logf("There is/are %d profile(s)", len(profiles))
	for _, profileName := range profiles {
		profile, err := cocs.ProfileRead(profileName)
		if err != nil {
			t.Fatalf("Unable to read profile %s %s", profile, err)
		}
		t.Logf("Profile %s: %v", profileName, profile)
	}
	pr := map[string]interface{}{
		"pool-limit": 99999999,
	}

	body, err := json.Marshal(pr)
	if err != nil {
		t.Logf("Bad json %s", err)
	}
	err = cocs.ProfileUpload("NOXIOUZTESTPROFILE", body)
	if err != nil {
		t.Logf("ProfileUplaod error %s", err)
	}

	err = cocs.ProfileUpload("NOXIOUZTESTPROFILE", []byte("notjson"))
	if err == nil {
		t.Fatal("Error expected, but nil")
	}

	err = cocs.ProfileRemove("NOXIOUZTESTPROFILE")
	if err != nil {
		t.Fatalf("ProfileRemove error %s", err)
	}

}

func TestHosts(t *testing.T) {
	// Create backend
	cocs := getTestCocaine(t)

	//List of hosts
	err := cocs.HostAdd("localhost")
	if err != nil {
		t.Fatalf("Error %s", err)
	}

	hosts, err := cocs.HostList()
	if err != nil {
		t.Fatalf("Error %s", err)
	}

	t.Logf("Hosts %v", hosts)
	if len(hosts) < 1 {
		t.Fatalf("Count of hosts less then 1 %d", len(hosts))
	}

	err = cocs.HostRemove("TESTHOST2")
	if err != nil {
		t.Fatalf("Error %s", err)
	}
}

func TestRunlists(t *testing.T) {
	cocs := getTestCocaine(t)

	//Runlists
	runlists, err := cocs.RunlistList()
	if err != nil {
		t.Fatalf("Error %s", err)
	}

	// Read every profile
	t.Logf("There is/are %d runlists(s)", len(runlists))
	for _, runlistName := range runlists {
		runlist, err := cocs.RunlistRead(runlistName)
		if err != nil {
			t.Fatalf("Unable to read runlist %s %s", runlist, err)
		}
		t.Logf("runlist %s: %v", runlistName, runlist)
	}
}

func TestGroups(t *testing.T) {
	cocs := getTestCocaine(t)

	//Groups
	err := cocs.GroupCreate("TESTGROUP")
	if err != nil {
		t.Fatalf("Error %s", err)
	}

	groups, err := cocs.GroupList()
	if err != nil {
		t.Fatalf("Error %s", err)
	}

	t.Logf("Groups count %v", groups)
	if len(groups) == 0 {
		t.Logf("Invalid group count %d", len(groups))
	}

	for _, groupName := range groups {
		group, err := cocs.GroupRead(groupName)
		if err != nil {
			t.Fatalf("Unable to read group %s %s", group, err)
		}
		t.Logf("group %s: %v", groupName, group)
	}

	err = cocs.GroupPushApp("TESTGROUP", "TESTAPP", 1)
	if err != nil {
		t.Fatal(err)
	}

	err = cocs.GroupPopApp("TESTGROUP", "TESTAPP")
	if err != nil {
		t.Fatal(err)
	}

	err = cocs.GroupRemove("TESTGROUP")
	if err != nil {
		t.Fatalf("Error %s", err)
	}

	t.SkipNow()

	err = cocs.GroupRefresh()
	if err != nil {
		t.Fatalf("All GroupRefresh error: %s", err)
	}

	err = cocs.GroupRefresh("TESTGROUP")
	if err != nil {
		t.Fatalf("GroupRefresh error: %s", err)
	}

	groups, err = cocs.GroupList()
	if err != nil {
		t.Fatalf("Error %s", err)
	}

	t.Logf("%v", groups)

}

func TestCrashlogs(t *testing.T) {
	cocs := getTestCocaine(t)

	//crashlogs
	crashlogs, err := cocs.CrashlogList("flow-tools")
	if err != nil {
		t.Fatal(err)
	}

	t.Logf("There is/are %d crashlogs", len(crashlogs))

	t.SkipNow()
	if len(crashlogs) > 0 {
		t.Log(crashlogs[0])
		ts, _ := strconv.Atoi(strings.Split(crashlogs[0], ":")[0])
		crash, err := cocs.CrashlogView(crashlogs[0], ts)
		if err != nil {
			t.Fatalf("CrashlogView error %s %s ", crashlogs[0], err)
		}
		t.Log(crash)
	}
}

func TestUpload(t *testing.T) {
	cocs := getTestCocaine(t)
	info := AppUplodaInfo{
		Path:    "/Users/noxiouz/Gotest/src/github.com/cocaine/cocaine-flow/test/testapp",
		App:     "bullet",
		Version: "first",
	}
	ch, status, err := cocs.ApplicationUpload(info)
	if err != nil {
		t.Fatalf("Error %s", err)
	}

	for lg := range ch {
		t.Log(lg)
	}

	if <-status != nil {
		t.Fatalf("Not uploaded")
	}

	apps, err := cocs.ApplicationList()
	if err != nil {
		t.Fatalf("ApplicationList error %s", err)
	}

	t.Logf("Apps %v", apps)

}

func TestBuildLog(t *testing.T) {
	cocs := getTestCocaine(t)

	buildlogs, err := cocs.BuildLogList()
	if err != nil {
		t.Fatalf("BuildLogList error %s", err)
	}

	t.Logf("Buildlogs: %s", buildlogs)

	for _, onelogid := range buildlogs {
		buildlog, err := cocs.BuildLogRead(onelogid)
		if err != nil {
			t.Fatalf("BuildLogRead %s error: %s", onelogid, err)
		}
		t.Logf("Build log: %s", buildlog)
	}
}

func TestAppOperations(t *testing.T) {
	cocs := getTestCocaine(t)

	r, err := cocs.ApplicationDeploy("bullet_first", "TEST", "FLOW")
	if err != nil {
		t.Fatalf("Error %s", err)
	}

	b, err := ioutil.ReadAll(r)
	if err != nil {
		t.Fatalf("Error %s", err)
	}
	t.Logf("Log: \n%s", b)

	r, err = cocs.ApplicationStart("bullet_first", "TEST")
	if err != nil {
		t.Fatalf("Error %s", err)
	}

	b, err = ioutil.ReadAll(r)
	if err != nil {
		t.Fatalf("Error %s", err)
	}

	t.Logf("Log: \n%s", b)

	r, err = cocs.ApplicationStop("bullet_first")
	if err != nil {
		t.Fatalf("Error %s", err)
	}

	b, err = ioutil.ReadAll(r)
	if err != nil {
		t.Fatalf("Error %s", err)
	}

	t.Logf("Log: \n%s", b)

	info, err := cocs.ApplicationInfo("flow-tools")
	if err != nil {
		t.Fatalf("Error %s", err)
	}

	t.Log(info)

}
