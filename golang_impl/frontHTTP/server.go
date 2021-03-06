package frontHTTP

import (
	"fmt"
	"io/ioutil"
	"log"
	"net/http"
	"os"
	"strconv"

	"github.com/gorilla/mux"
	"github.com/gorilla/sessions"

	"github.com/cocaine/cocaine-flow/backend"
	"github.com/cocaine/cocaine-flow/common"
	"github.com/cocaine/cocaine-flow/common/archive"
)

const pathPrefix = "/flow/v1"
const sessionName = "flow-session"

var (
	cocs  backend.AuthCocaine
	store *sessions.CookieStore //sessions.NewCookieStore(secretkey)
)

/*
	Profiles
*/

func ProfileList(cocs backend.Cocaine, w http.ResponseWriter, r *http.Request) {
	profiles, err := cocs.ProfileList()

	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	SendJson(w, profiles)
}

func ProfileRead(cocs backend.Cocaine, w http.ResponseWriter, r *http.Request) {
	name := mux.Vars(r)["name"]
	profile, err := cocs.ProfileRead(name)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	SendJson(w, profile)
}

func ProfileRemove(cocs backend.Cocaine, w http.ResponseWriter, r *http.Request) {
	name := mux.Vars(r)["name"]
	err := cocs.ProfileRemove(name)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	fmt.Fprintln(w, "OK")
}

func ProfileUpload(cocs backend.Cocaine, w http.ResponseWriter, r *http.Request) {
	name := mux.Vars(r)["name"]
	defer r.Body.Close()
	body, _ := ioutil.ReadAll(r.Body)
	if len(body) == 0 {
		http.Error(w, "Empty profile", http.StatusInternalServerError)
		return
	}

	err := cocs.ProfileUpload(name, body)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	fmt.Fprintln(w, "OK")
}

/*
	Hosts
*/

func HostList(cocs backend.Cocaine, w http.ResponseWriter, r *http.Request) {
	hosts, err := cocs.HostList()
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	SendJson(w, hosts)
}

func HostAdd(cocs backend.Cocaine, w http.ResponseWriter, r *http.Request) {
	host := mux.Vars(r)["host"]
	err := cocs.HostAdd(host)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	fmt.Fprint(w, "OK")
}

func HostRemove(cocs backend.Cocaine, w http.ResponseWriter, r *http.Request) {
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

func RunlistList(cocs backend.Cocaine, w http.ResponseWriter, r *http.Request) {
	runlists, err := cocs.RunlistList()
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	SendJson(w, runlists)
}

func RunlistRead(cocs backend.Cocaine, w http.ResponseWriter, r *http.Request) {
	name := mux.Vars(r)["name"]
	runlist, err := cocs.RunlistRead(name)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	SendJson(w, runlist)
}

func RunlistRemove(cocs backend.Cocaine, w http.ResponseWriter, r *http.Request) {
	name := mux.Vars(r)["name"]
	err := cocs.RunlistRemove(name)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	fmt.Fprint(w, "OK")
}

/*
	Groups
*/

func GroupList(cocs backend.Cocaine, w http.ResponseWriter, r *http.Request) {
	runlists, err := cocs.GroupList()
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	SendJson(w, runlists)
}

func GroupRead(cocs backend.Cocaine, w http.ResponseWriter, r *http.Request) {
	name := mux.Vars(r)["name"]
	group, err := cocs.GroupRead(name)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	SendJson(w, group)
}

func GroupCreate(cocs backend.Cocaine, w http.ResponseWriter, r *http.Request) {
	name := mux.Vars(r)["name"]
	err := cocs.GroupCreate(name)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	fmt.Fprint(w, "OK")
}

func GroupRemove(cocs backend.Cocaine, w http.ResponseWriter, r *http.Request) {
	name := mux.Vars(r)["name"]
	err := cocs.GroupRemove(name)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	fmt.Fprint(w, "OK")
}

func GroupPushApp(cocs backend.Cocaine, w http.ResponseWriter, r *http.Request) {
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

func GroupPopApp(cocs backend.Cocaine, w http.ResponseWriter, r *http.Request) {
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

func GroupRefresh(cocs backend.Cocaine, w http.ResponseWriter, r *http.Request) {
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

	if len(name) == 0 || len(password) == 0 {
		http.Error(w, "name or password parametr is missing", http.StatusBadRequest)
		return
	}

	if err := cocs.UserSignup(name, password); err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	fmt.Fprint(w, "OK")
}

func UserSignin(w http.ResponseWriter, r *http.Request) {
	name := r.FormValue("name")
	password := r.FormValue("password")

	if len(name) == 0 || len(password) == 0 {
		http.Error(w, "name or password parametr is missing", http.StatusBadRequest)
		return
	}

	if _, err := cocs.UserSignin(name, password); err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	session, _ := store.Get(r, sessionName)

	session.Values["name"] = name
	session.Values["password"] = password
	store.Save(r, w, session)

	fmt.Fprint(w, "OK")
}

func GenToken(w http.ResponseWriter, r *http.Request) {
	name := r.FormValue("name")
	password := r.FormValue("password")

	if len(name) == 0 || len(password) == 0 {
		http.Error(w, "name or password parametr is missing", http.StatusBadRequest)
		return
	}

	token, err := cocs.GenToken(name, password)
	if err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}
	fmt.Fprint(w, token)
}

/*
	Crashlogs
*/

func CrashlogList(cocs backend.Cocaine, w http.ResponseWriter, r *http.Request) {
	name := mux.Vars(r)["name"]

	crashlogs, err := cocs.CrashlogList(name)
	if err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}
	SendJson(w, crashlogs)
}

func CrashlogView(cocs backend.Cocaine, w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	name := vars["name"]
	timestamp, err := strconv.Atoi(vars["timestamp"])
	if err != nil {
		http.Error(w, "timestamp must be a number", http.StatusBadRequest)
		return
	}

	crashlog, err := cocs.CrashlogView(name, timestamp)
	if err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}
	fmt.Fprintf(w, crashlog)
}

/*
	Buildlog
*/

func BuildLogList(cocs backend.Cocaine, w http.ResponseWriter, r *http.Request) {
	buildlogs, err := cocs.BuildLogList()
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	SendJson(w, buildlogs)
}

func BuildLogRead(cocs backend.Cocaine, w http.ResponseWriter, r *http.Request) {
	id := mux.Vars(r)["id"]

	buildlog, err := cocs.BuildLogRead(id)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	fmt.Fprintf(w, buildlog)
}

/*
	Application
*/

func ApplicationList(cocs backend.Cocaine, w http.ResponseWriter, r *http.Request) {
	apps, err := cocs.ApplicationList()
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	SendJson(w, apps)
}

func ApplicationUpload(cocs backend.Cocaine, w http.ResponseWriter, r *http.Request) {
	name := mux.Vars(r)["name"]
	version := mux.Vars(r)["version"]

	defer r.Body.Close()
	path, err := archive.Unpack(r.Body)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	defer os.RemoveAll(path)

	info := backend.AppUplodaInfo{
		Path:    path,
		App:     name,
		Version: version,
	}

	ch, _, err := cocs.ApplicationUpload(info)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	for lg := range ch {
		w.Write([]byte(lg))
		w.(http.Flusher).Flush()
	}
}

func ApplicationStart(cocs backend.Cocaine, w http.ResponseWriter, r *http.Request) {
	name := r.FormValue("name")
	profile := r.FormValue("profile")

	if len(name) == 0 || len(profile) == 0 {
		http.Error(w, "name or profile wasn't specified", http.StatusInternalServerError)
		return
	}

	stream, err := cocs.ApplicationStart(name, profile)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	if f, ok := w.(http.Flusher); !ok {
		for {
			var p []byte
			_, err := stream.Read(p)
			fmt.Println(p, err)
			if err != nil {
				break
			}
			w.Write(p)
			f.Flush()
		}
	} else {
		body, _ := ioutil.ReadAll(stream)
		fmt.Fprintf(w, "%s", body)
	}
}

/*

*/

func ConstructHandler() http.Handler {
	var err error
	cocs, err = backend.NewBackend()
	if err != nil {
		log.Fatalln(err)
	}

	context, err := common.GetContext()
	if err != nil {
		log.Fatalln(err)
	}

	store = sessions.NewCookieStore(context.SecretKey())

	//main router
	router := mux.NewRouter()
	router.StrictSlash(true)
	router.HandleFunc("/ping", Ping)

	//flow router
	rootRouter := router.PathPrefix(pathPrefix).Subrouter()

	//profiles router
	profilesRouter := rootRouter.PathPrefix("/profiles").Subrouter()
	profilesRouter.StrictSlash(true)
	profilesRouter.HandleFunc("/", Guest(ProfileList)).Methods("GET")
	profilesRouter.HandleFunc("/{name}", AuthRequired(ProfileRead)).Methods("GET")
	profilesRouter.HandleFunc("/{name}", AuthRequired(ProfileUpload)).Methods("PUT", "POST")
	profilesRouter.HandleFunc("/{name}", AuthRequired(ProfileRemove)).Methods("DELETE")

	//hosts router
	hostsRouter := rootRouter.PathPrefix("/hosts").Subrouter()
	hostsRouter.HandleFunc("/", AuthRequired(HostList)).Methods("GET")
	hostsRouter.HandleFunc("/{host}", AuthRequired(HostAdd)).Methods("POST", "PUT")
	hostsRouter.HandleFunc("/{host}", AuthRequired(HostRemove)).Methods("DELETE")

	//runlists router
	runlistsRouter := rootRouter.PathPrefix("/runlists").Subrouter()
	runlistsRouter.StrictSlash(true)
	runlistsRouter.HandleFunc("/", AuthRequired(RunlistList)).Methods("GET")
	runlistsRouter.HandleFunc("/{name}", AuthRequired(RunlistRead)).Methods("GET")
	runlistsRouter.HandleFunc("/{name}", AuthRequired(RunlistRemove)).Methods("DELETE")

	//routing groups
	groupsRouter := rootRouter.PathPrefix("/groups").Subrouter()
	groupsRouter.StrictSlash(true)
	groupsRouter.HandleFunc("/", AuthRequired(GroupList)).Methods("GET")
	groupsRouter.HandleFunc("/{name}", AuthRequired(GroupRead)).Methods("GET")
	groupsRouter.HandleFunc("/{name}", AuthRequired(GroupCreate)).Methods("POST")
	groupsRouter.HandleFunc("/{name}", AuthRequired(GroupRemove)).Methods("DELETE")

	groupsRouter.HandleFunc("/{name}/{app}", AuthRequired(GroupPushApp)).Methods("POST", "PUT")
	groupsRouter.HandleFunc("/{name}/{app}", AuthRequired(GroupPopApp)).Methods("DELETE")

	rootRouter.HandleFunc("/groupsrefresh/", AuthRequired(GroupRefresh)).Methods("POST")
	rootRouter.HandleFunc("/groupsrefresh/{name}", AuthRequired(GroupRefresh)).Methods("POST")

	//crashlog router
	crashlogRouter := rootRouter.PathPrefix("/crashlogs").Subrouter()
	crashlogRouter.StrictSlash(true)
	crashlogRouter.HandleFunc("/{name}", AuthRequired(CrashlogList)).Methods("GET")
	crashlogRouter.HandleFunc("/{name}/{timestamp}", AuthRequired(CrashlogView)).Methods("GET")
	// crashlogRouter.HandleFunc("/{name}/{timestamp}", AuthRequired(CrashlogRemove)).Methods("DELETE")

	//auth router
	authRouter := rootRouter.PathPrefix("/users").Subrouter()
	authRouter.StrictSlash(true)
	authRouter.HandleFunc("/token", GenToken).Methods("POST")
	authRouter.HandleFunc("/signup", UserSignup).Methods("POST")
	authRouter.HandleFunc("/signin", UserSignin).Methods("POST")

	//buildlog router
	buildlogRouter := rootRouter.PathPrefix("/buildlog").Subrouter()
	buildlogRouter.StrictSlash(true)
	buildlogRouter.HandleFunc("/", AuthRequired(BuildLogList)).Methods("GET")
	buildlogRouter.HandleFunc("/{id}", AuthRequired(BuildLogRead)).Methods("GET")

	//app router
	appRouter := rootRouter.PathPrefix("/app/").Subrouter()
	appRouter.StrictSlash(true)
	appRouter.HandleFunc("/", AuthRequired(ApplicationList)).Methods("GET")
	appRouter.HandleFunc("/{name}/{version}", AuthRequired(ApplicationUpload)).Methods("POST", "PUT")
	appRouter.HandleFunc("/start", AuthRequired(ApplicationStart)).Methods("POST", "PUT")
	// appRouter.HandleFunc("/stop", AuthRequired(ApplicationStop)).Methods("POST", "PUT")

	//return handlers.LoggingHandler(os.Stdout, router)
	router.PathPrefix("/").Handler(http.FileServer(http.Dir("./static/")))
	return router
}
