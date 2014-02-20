package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"

	"github.com/gorilla/handlers"
	"github.com/gorilla/mux"
	"github.com/gorilla/sessions"
)

const pathPrefix = "/flow/v1"
const sessionName = "flow-session"

var (
	cocs  Cocaine
	store = sessions.NewCookieStore([]byte("something-very-secret"))
)

var jsonOK = map[string]string{
	"status": "OK",
}

/*
	Utils
*/

func SendError(w http.ResponseWriter, err error, code int) {
	w.WriteHeader(http.StatusNotFound)
	fmt.Fprint(w, err)
}

func SendJson(w http.ResponseWriter, data interface{}) (err error) {
	w.Header().Set("Content-Type", "application/json")
	err = json.NewEncoder(w).Encode(data)
	return
}

func Ping(w http.ResponseWriter, r *http.Request) {
	fmt.Fprintln(w, "OK")
}

func Test(w http.ResponseWriter, r *http.Request) {
	session, ok := store.Get(r, "flow-session")
	fmt.Println(session, ok)
	// Set some session values.
	session.Values["foo"] = "bar"
	session.Values[42] = 43
	// Save it.
	session.Save(r, w)
	fmt.Fprintln(w, "OK")
}

func ConstructHandler() http.Handler {
	var err error
	cocs, err = NewBackend()
	if err != nil {
		log.Fatalln(err)
	}

	//main router
	router := mux.NewRouter()
	router.HandleFunc("/ping", Ping)
	router.HandleFunc("/test", Test)

	//flow router
	rootRouter := router.PathPrefix(pathPrefix).Subrouter()

	//profiles router
	profilesRouter := rootRouter.PathPrefix("/profiles").Subrouter()
	profilesRouter.HandleFunc("/", ProfileList).Methods("GET")
	profilesRouter.HandleFunc("/{name}", ProfileRead).Methods("GET")

	//hosts router
	hostsRouter := rootRouter.PathPrefix("/hosts").Subrouter()
	hostsRouter.HandleFunc("/", HostList).Methods("GET")
	hostsRouter.HandleFunc("/{host}", HostAdd).Methods("POST", "PUT")
	hostsRouter.HandleFunc("/{host}", HostRemove).Methods("DELETE")

	//runlists router
	runlistsRouter := rootRouter.PathPrefix("/runlists").Subrouter()
	runlistsRouter.HandleFunc("/", RunlistList).Methods("GET")
	runlistsRouter.HandleFunc("/{name}", RunlistRead).Methods("GET")

	//routing groups

	return handlers.LoggingHandler(os.Stdout, router)
}

/*
	Profiles
*/

func ProfileList(w http.ResponseWriter, r *http.Request) {
	profiles, err := cocs.ProfileList()

	if err != nil {
		SendError(w, err, http.StatusInternalServerError)
	}

	SendJson(w, profiles)
}

func ProfileRead(w http.ResponseWriter, r *http.Request) {
	name := mux.Vars(r)["name"]
	profile, err := cocs.ProfileRead(name)
	if err != nil {
		SendError(w, err, http.StatusInternalServerError)
		return
	}

	SendJson(w, profile)
}

/*
	Hosts
*/

func HostList(w http.ResponseWriter, r *http.Request) {
	hosts, err := cocs.HostList()
	if err != nil {
		SendError(w, err, http.StatusInternalServerError)
	}

	SendJson(w, hosts)
}

func HostAdd(w http.ResponseWriter, r *http.Request) {
	host := mux.Vars(r)["host"]
	err := cocs.HostAdd(host)
	if err != nil {
		SendError(w, err, http.StatusInternalServerError)
	}

	fmt.Fprint(w, "OK")
}

func HostRemove(w http.ResponseWriter, r *http.Request) {
	host := mux.Vars(r)["host"]
	err := cocs.HostRemove(host)
	if err != nil {
		SendError(w, err, http.StatusInternalServerError)
	}

	fmt.Fprint(w, "OK")
}

/*
	Runlists
*/

func RunlistList(w http.ResponseWriter, r *http.Request) {
	runlists, err := cocs.RunlistList()
	if err != nil {
		SendError(w, err, http.StatusInternalServerError)
		return
	}

	SendJson(w, runlists)
}

func RunlistRead(w http.ResponseWriter, r *http.Request) {
	name := mux.Vars(r)["name"]
	runlist, err := cocs.RunlistRead(name)
	if err != nil {
		SendError(w, err, http.StatusInternalServerError)
		return
	}

	SendJson(w, runlist)
}

func main() {
	h := ConstructHandler()
	log.Fatalln(http.ListenAndServe(":8080", h))
}
