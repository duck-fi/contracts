FROM alpine as builder
WORKDIR /var/lib/dispersion
RUN apk add --no-cache musl-dev linux-headers python3-dev gcc py-pip nodejs npm && \
    pip install eth-brownie && npm install -g ganache-cli
ADD contracts contracts
ADD interfaces interfaces
ADD scripts scripts
ADD brownie-config.yaml brownie-config.yaml
ADD requirements.txt requirements.txt
RUN ganache-cli --db /var/lib/dispersion/db -m "abstract render give egg now oxygen wisdom extend strategy link risk insane" > node-logs.txt & sleep 5 & brownie run development deploy > deploy-logs.txt

RUN python3 scripts/blockscout.py

FROM forestfriends/blockscout:postgres
COPY --from=builder contracts.sql /docker-entrypoint-initdb.d/1-contracts.sql