package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"strconv"

	"github.com/gorilla/handlers"
	"github.com/gorilla/mux"
	"github.com/gorilla/sessions"
)

const pathPrefix = "/flow/v1"
const sessionName = "flow-session"

var (
	// TBD: Read it from file
	secretkey = []byte("something-very-secretkeysddsddsd")
	cocs      Cocaine
	store     = sessions.NewCookieStore(secretkey)
)

var jsonOK = map[string]string{
	"status": "OK",
}

/*
	Utils
*/

func ExtractToken(r *http.Request) (token string) {
	tokens, ok := r.URL.Query()["token"]
	if ok {
		token = tokens[len(tokens)-1]
	}
	return
}

func SendJson(w http.ResponseWriter, data interface{}) (err error) {
	w.Header().Set("Content-Type", "application/json")
	err = json.NewEncoder(w).Encode(data)
	return
}

func Ping(w http.ResponseWriter, r *http.Request) {
	fmt.Fprintln(w, "OK")
}

func AuthRequired(fn func(w http.ResponseWriter, r *http.Request)) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		//Check token auth
		token := ExtractToken(r)
		_, err := cocs.ValidateToken(token)
		if err != nil {
			http.Error(w, err.Error(), http.StatusUnauthorized)
			return
		}
		fn(w, r)
	}

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
	router.HandleFunc("/ping", AuthRequired(Ping))
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
	groupsRouter := rootRouter.PathPrefix("/groups").Subrouter()
	groupsRouter.HandleFunc("/", GroupList).Methods("GET")
	groupsRouter.HandleFunc("/{name}", GroupView).Methods("GET")
	groupsRouter.HandleFunc("/{name}", GroupCreate).Methods("POST")
	groupsRouter.HandleFunc("/{name}", GroupRemove).Methods("DELETE")

	groupsRouter.HandleFunc("/{name}/{app}", GroupPushApp).Methods("POST", "PUT")
	groupsRouter.HandleFunc("/{name}/{app}", GroupPopApp).Methods("DELETE")

	rootRouter.HandleFunc("/groupsrefresh/", GroupRefresh).Methods("POST")
	rootRouter.HandleFunc("/groupsrefresh/{name}", GroupRefresh).Methods("POST")

	//auth router
	authRouter := rootRouter.PathPrefix("/users").Subrouter()
	authRouter.HandleFunc("/token", GenToken).Methods("POST")
	authRouter.HandleFunc("/signup", UserSignup).Methods("POST")
	authRouter.HandleFunc("/signin", UserSignin).Methods("POST")

	return handlers.LoggingHandler(os.Stdout, router)
}

/*
	Profiles
*/

func ProfileList(w http.ResponseWriter, r *http.Request) {
	profiles, err := cocs.ProfileList()

	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	SendJson(w, profiles)
}

func ProfileRead(w http.ResponseWriter, r *http.Request) {
	name := mux.Vars(r)["name"]
	profile, err := cocs.ProfileRead(name)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
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
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	SendJson(w, hosts)
}

func HostAdd(w http.ResponseWriter, r *http.Request) {
	host := mux.Vars(r)["host"]
	err := cocs.HostAdd(host)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	fmt.Fprint(w, "OK")
}

func HostRemove(w http.ResponseWriter, r *http.Request) {
	host := mux.Vars(r)["host"]
	err := cocs.HostRemove(host)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	fmt.Fprint(w, "OK")
}

/*
	Runlists
*/

func RunlistList(w http.ResponseWriter, r *http.Request) {
	runlists, err := cocs.RunlistList()
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	SendJson(w, runlists)
}

func RunlistRead(w http.ResponseWriter, r *http.Request) {
	name := mux.Vars(r)["name"]
	runlist, err := cocs.RunlistRead(name)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	SendJson(w, runlist)
}

/*
	Groups
*/

func GroupList(w http.ResponseWriter, r *http.Request) {
	runlists, err := cocs.GroupList()
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	SendJson(w, runlists)
}

func GroupView(w http.ResponseWriter, r *http.Request) {
	name := mux.Vars(r)["name"]
	group, err := cocs.GroupView(name)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	SendJson(w, group)
}

func GroupCreate(w http.ResponseWriter, r *http.Request) {
	name := mux.Vars(r)["name"]
	err := cocs.GroupCreate(name)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	fmt.Fprint(w, "OK")
}

func GroupRemove(w http.ResponseWriter, r *http.Request) {
	name := mux.Vars(r)["name"]
	err := cocs.GroupRemove(name)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	fmt.Fprint(w, "OK")
}

func GroupPushApp(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)

	name := vars["name"]
	app := vars["app"]
	weights, ok := r.URL.Query()["weight"]
	if !ok || len(weights) == 0 {
		http.Error(w, "weight argument is absent", http.StatusBadRequest)
		return
	}

	weight, err := strconv.Atoi(weights[0])
	if err != nil {
		http.Error(w, "weight must be an integer value", http.StatusBadRequest)
		return
	}

	err = cocs.GroupPushApp(name, app, weight)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	fmt.Fprint(w, "OK")
}

func GroupPopApp(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	name := vars["name"]
	app := vars["app"]

	err := cocs.GroupPopApp(name, app)
	if err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}
	fmt.Fprint(w, "OK")
}

func GroupRefresh(w http.ResponseWriter, r *http.Request) {
	name := mux.Vars(r)["name"]

	err := cocs.GroupRefresh(name)
	if err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}
	fmt.Fprint(w, "OK")
}

/*
	Auth
*/

func UserSignup(w http.ResponseWriter, r *http.Request) {
	name := r.FormValue("name")
	password := r.FormValue("password")
	if err := cocs.UserSignup(name, password); err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	fmt.Fprint(w, "OK")
}

func UserSignin(w http.ResponseWriter, r *http.Request) {
	name := r.FormValue("name")
	password := r.FormValue("password")
	if _, err := cocs.UserSignin(name, password); err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	fmt.Fprint(w, "OK")
}

func GenToken(w http.ResponseWriter, r *http.Request) {
	name := r.FormValue("name")
	password := r.FormValue("password")
	token, err := cocs.GenToken(name, password)
	if err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}
	fmt.Fprint(w, token)
}

func main() {
	h := ConstructHandler()
	log.Fatalln(http.ListenAndServe(":8080", h))
}
