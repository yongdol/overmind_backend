import binascii
import json
from Crypto.PublicKey import RSA
import urllib

prvkey_json = urllib.urlopen("http://172.31.40.238:8081/get-prvkey").read()
prvkey_dict = json.loads(prvkey_json)
#print prvkey_dict
prvkey = prvkey_dict['prvkey']
#prvkey = open("ff_key","rb").read()
#pubkey = open("ff_key.pub","rb").read()
#print prvkey
prvkeyObj = RSA.importKey(prvkey)
#pubkeyObj = RSA.importKey(pubkey)
#msg = "attack at dawn"
#emsg = binascii.hexlify(pubkeyObj.encrypt(msg,'x')[0])
cred_json = json.loads(open("my_job_info.json","r").read())
emsg = cred_json['creds']['cred_acc_no']
print emsg

dmsg = prvkeyObj.decrypt(binascii.unhexlify(emsg))
print dmsg
