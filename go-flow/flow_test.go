package main

import (
	"testing"
)

func TestMain(t *testing.T) {
	// Create backend
	b, err := NewBackend()
	if err != nil {
		t.Fatalf("Unable to create backend %s ", err)
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
