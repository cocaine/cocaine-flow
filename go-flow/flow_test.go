package main

import (
	"testing"
)

const testUser = "noxiouz"
const testUserPasswd = "qwerty"

func TestMain(t *testing.T) {
	// Create backend
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

	ui, err := b.UserSignin(testUser, testUserPasswd)
	if err != nil {
		t.Fatal(err)
	}

	token, err := b.GenToken(testUser, testUserPasswd)
	if err != nil {
		t.Fatal(err)
	}

	t.Logf("Token %s", token)

	ui2, err := b.ValidateToken(token)
	if err != nil || ui2.Name != ui.Name {
		t.Logf("Bad token %s", err)
	}

	t.Log(ui)

	err = b.UserRemove(testUser)
	if err != nil {
		t.Fatal(err)
	}

	// List of profiles
	profiles, err := b.ProfileList()
	if err != nil {
		t.Fatalf("Unable to get list of profiles %s", err)
	}

	// Read every profile
	t.Logf("There is/are %d profile(s)", len(profiles))
	for _, profileName := range profiles {
		profile, err := b.ProfileRead(profileName)
		if err != nil {
			t.Fatalf("Unable to read profile %s %s", profile, err)
		}
		t.Logf("Profile %s: %v", profileName, profile)
	}

	//List of hosts
	err = b.HostAdd("TESTHOST")
	if err != nil {
		t.Fatalf("Error %s", err)
	}

	hosts, err := b.HostList()
	if err != nil {
		t.Fatalf("Error %s", err)
	}

	t.Logf("Hosts %v", hosts)
	if len(hosts) < 1 {
		t.Fatalf("Count of hosts less then 1 %d", len(hosts))
	}

	err = b.HostRemove("TESTHOST2")
	if err != nil {
		t.Fatalf("Error %s", err)
	}

	//Runlists
	runlists, err := b.RunlistList()
	if err != nil {
		t.Fatalf("Error %s", err)
	}

	// Read every profile
	t.Logf("There is/are %d runlists(s)", len(runlists))
	for _, runlistName := range runlists {
		runlist, err := b.RunlistRead(runlistName)
		if err != nil {
			t.Fatalf("Unable to read runlist %s %s", runlist, err)
		}
		t.Logf("runlist %s: %v", runlistName, runlist)
	}

	//Groups
	err = b.GroupCreate("TESTGROUP")
	if err != nil {
		t.Fatalf("Error %s", err)
	}

	groups, err := b.GroupList()
	if err != nil {
		t.Fatalf("Error %s", err)
	}

	t.Logf("Groups count %v", groups)
	if len(groups) == 0 {
		t.Logf("Invalid group count %d", len(groups))
	}

	for _, groupName := range groups {
		group, err := b.GroupView(groupName)
		if err != nil {
			t.Fatalf("Unable to read group %s %s", group, err)
		}
		t.Logf("runlist %s: %v", groupName, group)
	}

	err = b.GroupPushApp("TESTGROUP", "TESTAPP", 1)
	if err != nil {
		t.Fatal(err)
	}

	err = b.GroupPopApp("TESTGROUP", "TESTAPP")
	if err != nil {
		t.Fatal(err)
	}

	err = b.GroupRemove("TESTGROUP")
	if err != nil {
		t.Fatalf("Error %s", err)
	}

	groups, err = b.GroupList()
	if err != nil {
		t.Fatalf("Error %s", err)
	}

	t.Logf("%v", groups)

}

func TestCrashlogs(t *testing.T) {
	b, err := NewBackend()
	if err != nil {
		t.Fatalf("Unable to create backend %s ", err)
	}

	//crashlogs
	crashlogs, err := b.CrashlogList("flow-tools")
	if err != nil {
		t.Fatal(err)
	}

	t.Logf("There is/are %d crashlog", len(crashlogs))

	if len(crashlogs) > 0 {
		t.Log(crashlogs[0])
		crash, err := b.CrashlogView(crashlogs[0], 1392638415086578)
		if err != nil {
			t.Fatal(err)
		}
		t.Log(crash)
	}
}
