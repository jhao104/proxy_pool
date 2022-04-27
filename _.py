import json

a = '{"name":"🇦🇺AU_66","server":"129.154.54.75","type":"vmess","country":"🇦🇺AU","port":33004,"uuid":"4f14695c-31b9-45bf-ca34-1d82170fc100","alterId":0,"cipher":"auto","network":"ws","ws-path":"/","http-opts":{},"h2-opts":{},"skip-cert-verify":true}'

print(type(json.loads(a)))