package backend

import (
	"crypto/cipher"
	"crypto/rand"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"time"
)

const token_lifetime = 3600 // sec

type Tokenhandler interface {
	Encrypt(*UserInfo) (string, error)
	Decrypt(string) (UserInfo, error)
}

type Token struct {
	block cipher.Block
}

type tokenWrapper struct {
	UI       *UserInfo
	Lifetime int64
}

func (t *Token) Encrypt(ui *UserInfo) (tok string, err error) {
	elapsedTime := time.Now().Add(time.Second * token_lifetime).Unix()
	value, err := json.Marshal(tokenWrapper{ui, elapsedTime})
	if err != nil {
		return
	}

	iv := make([]byte, t.block.BlockSize())
	rand.Read(iv)

	stream := cipher.NewCTR(t.block, iv)
	stream.XORKeyStream(value, value)
	tok = hex.EncodeToString(append(iv, value...))
	return
}

func (t *Token) Decrypt(tok string) (ui UserInfo, err error) {

	value, err := hex.DecodeString(tok)
	if err != nil {
		err = fmt.Errorf("Corrupted token")
		return
	}

	if len(value) < t.block.BlockSize() {
		err = fmt.Errorf("Too short to be decrypted, %d", len(value))
		return
	}

	iv := value[:t.block.BlockSize()]
	value = value[t.block.BlockSize():]
	stream := cipher.NewCTR(t.block, iv)
	stream.XORKeyStream(value, value)

	var wui tokenWrapper
	err = json.Unmarshal(value, &wui)
	if err != nil {
		return
	}

	elapsedTime := time.Unix(wui.Lifetime, 0)
	if time.Now().After(elapsedTime) {
		err = fmt.Errorf("Token has expired")
		return
	}

	ui = *wui.UI
	return
}
