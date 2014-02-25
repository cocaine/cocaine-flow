package backend

import (
	"log"

	"github.com/ugorji/go/codec"

	"github.com/cocaine/cocaine-framework-go/cocaine"
)

var (
	mh codec.MsgpackHandle
	h  = &mh
)

/*
	Application helper
*/

type appWrapper interface {
	Call(method string, args interface{}, result ...interface{}) (err error)
}

type wrappedApp struct {
	app *cocaine.Service
}

func (aW *wrappedApp) Call(method string, args interface{}, result ...interface{}) (err error) {
	var buf []byte
	err = codec.NewEncoderBytes(&buf, h).Encode(args)
	if err != nil {
		return
	}

	res, isOpen := <-aW.app.Call("enqueue", method, buf)
	if !isOpen {
		return nil
	}

	err = res.Err()
	if err != nil {
		return
	}

	if len(result) == 1 {
		err = res.Extract(result[0])
	}
	return
}

func NewAppWrapper(name string) (wa appWrapper, err error) {
	app, err := cocaine.NewService("flow-tools")
	if err != nil {
		log.Printf("Error %s", err)
		return nil, err
	}
	wa = &wrappedApp{app}
	return
}
