package backend

import (
	"strconv"
	"strings"
	"testing"

	"github.com/cocaine/cocaine-flow/common"
)

const testUser = "noxiouz"
const testUserPasswd = "qwerty"
const testDocker = "http://192.168.1.150:3138"
const testCocaine = ":10053"
const testRegistry = "192.168.1.150:5000"

func createContext() {
	cfg := common.ContextCfg{
		Docker:   testDocker,
		Registry: testRegistry,
		Cocaine:  testCocaine,
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

	t.Logf("Token %s", token)

	_, err = b.UserSignin(testUser, testUserPasswd)
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
}

func TestHosts(t *testing.T) {
	// Create backend
	cocs := getTestCocaine(t)

	//List of hosts
	err := cocs.HostAdd("TESTHOST")
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
		group, err := cocs.GroupView(groupName)
		if err != nil {
			t.Fatalf("Unable to read group %s %s", group, err)
		}
		t.Logf("runlist %s: %v", groupName, group)
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

	if len(crashlogs) > 0 {
		t.Log(crashlogs[0])
		ts, _ := strconv.Atoi(strings.Split(crashlogs[0], ":")[0])
		crash, err := cocs.CrashlogView(crashlogs[0], ts)
		if err != nil {
			t.Fatal(err)
		}
		t.Log(crash)
	}
}

func TestUpload(t *testing.T) {
	cocs := getTestCocaine(t)
	ch, status, err := cocs.ApplicationUpload(testUser, "bullet", "/Users/noxiouz/Gotest/src/github.com/cocaine/cocaine-flow/flow")
	if err != nil {
		t.Fatalf("Error %s", err)
	}

	for lg := range ch {
		t.Log(lg)
	}

	if !(*status) {
		t.Fatalf("Not uploaded")
	}
}
