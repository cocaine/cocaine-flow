package frontHTTP

import (
	"encoding/json"
	"fmt"
	"net/http"

	"github.com/cocaine/cocaine-flow/backend"
)

var jsonOK = map[string]string{
	"status": "OK",
}

/*
	Utils
*/

func extractToken(r *http.Request) (token string) {
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

func AuthRequired(fn func(cocs backend.Cocaine, w http.ResponseWriter, r *http.Request)) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		if session, ok := store.Get(r, sessionName); ok != nil {

			name, isString := session.Values["name"].(string)
			if !isString {
				http.Error(w, "Corrupted cookies", http.StatusUnauthorized)
				return
			}

			password, isString := session.Values["password"].(string)
			if !isString {
				http.Error(w, "Corrupted cookies", http.StatusUnauthorized)
				return
			}

			c, err := cocs.UserSignin(name, password)
			if err != nil {
				http.Error(w, err.Error(), http.StatusUnauthorized)
				return
			}

			fn(c, w, r)
			return
		}

		if token := extractToken(r); len(token) > 0 {
			c, err := cocs.ValidateToken(token)
			if err != nil {
				http.Error(w, err.Error(), http.StatusUnauthorized)
				return
			}

			fn(c, w, r)
			return
		}
	}
}

func Guest(fn func(cocs backend.Cocaine, w http.ResponseWriter, r *http.Request)) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		c, err := cocs.GuestAccount()
		if err != nil {
			http.Error(w, err.Error(), http.StatusUnauthorized)
			return
		}
		fn(c, w, r)
	}
}
