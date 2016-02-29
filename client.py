# chat_client.py

import sys, socket, select
import base64
from Crypto.Cipher import AES
from Crypto import Random
import hashlib
import getpass

BLOCKSIZE = 16
pad = lambda s: s + (BLOCKSIZE - len(s) % BLOCKSIZE) * chr(BLOCKSIZE - len(s) % BLOCKSIZE)
unpad = lambda s: s[:-ord(s[len(s)-1:])]

def encrypt(key, raw):
	if key == '':
		return raw

	key = hashlib.sha256(key.encode()).digest()
	raw = pad(raw)
	IV = Random.new().read(AES.block_size)
	cipher = AES.new(key, AES.MODE_CBC, IV)
	return base64.b64encode(IV + cipher.encrypt(raw))

def decrypt(key, encoding):
	if key == '':
		return encoding
	key = hashlib.sha256(key.encode()).digest()
	encoding = base64.b64decode(encoding)
	IV = encoding[:16]
	cipher = AES.new(key, AES.MODE_CBC, IV)
	return unpad(cipher.decrypt(encoding[16:]))
	
 
def chat_client():
    if(len(sys.argv) < 3) :
        print 'Usage : python chat_client.py hostname port'
        sys.exit()

    host = sys.argv[1]
    port = int(sys.argv[2])
     
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)

    name = raw_input('Enter your name: ')
    key = raw_input('Enter secret key: ')
     
    # connect to remote host
    try :
        s.connect((host, port))
    except :
        print 'Unable to connect'
        sys.exit()
     
    print 'Connected to remote host. You can start sending messages'
    sys.stdout.write('[Me] '); sys.stdout.flush()
     
    while 1:
        socket_list = [sys.stdin, s]
         
        # Get the list sockets which are readable
        read_sockets, write_sockets, error_sockets = select.select(socket_list , [], [])
         
        for sock in read_sockets:            
            if sock == s:
                # incoming message from remote server, s
                data = sock.recv(4096)
                data = decrypt(key, data)
                if not data :
                    print '\nDisconnected from chat server'
                    sys.exit()
                else :
                    #print data
                    sys.stdout.write(data)
                    sys.stdout.write('[Me] '); sys.stdout.flush()     
            
            else :
                # user entered a message
                msg = sys.stdin.readline()
                msg = '[%s] %s\n' % (name, msg)
                msg = encrypt(key, msg)
				# encrypt and send the message
                s.send(msg)
                sys.stdout.write('[Me] '); sys.stdout.flush() 

if __name__ == "__main__":
    sys.exit(chat_client())
