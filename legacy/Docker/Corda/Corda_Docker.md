```shell
docker run -ti --net="host" \
        -e MY_LEGAL_NAME="O=Quincy,L=Jones,C=DE"     \
        -e MY_PUBLIC_ADDRESS="corda.example-hoster.com"       \
        -e NETWORKMAP_URL="https://map.corda.example.com"    \
        -e DOORMAN_URL="https://doorman.corda.example.com"      \
        -e NETWORK_TRUST_PASSWORD="Quincy2222"       \
        -e MY_EMAIL_ADDRESS="rqjones@asu.edu"      \
        -e SSHPORT="22"      \
        -e RPC_USER="Q"      \
        -v /home/user/docker/config:/etc/corda          \
        -v /home/user/docker/certificates:/opt/corda/certificates \
        corda/corda-zulu-java1.8-4.7:latest config-generator --generic --exit-on-generate
```

