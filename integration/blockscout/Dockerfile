FROM alpine as builder
WORKDIR /var/lib/dispersion
RUN apk add --no-cache musl-dev linux-headers python3-dev gcc py-pip nodejs npm && \
    pip install eth-brownie && npm install -g ganache-cli
ADD contracts contracts
ADD interfaces interfaces
ADD scripts scripts
ADD integration integration
ADD brownie-config.yaml brownie-config.yaml
ADD requirements.txt requirements.txt
RUN ganache-cli --db /var/lib/dispersion/db -m "abstract render give egg now oxygen wisdom extend strategy link risk insane" > node-logs.txt & sleep 5 & brownie run development deploy | sed 's/\x1B\[[0-9;]\{1,\}[A-Za-z]//g' > deploy-logs.txt
RUN cat -v deploy-logs.txt | sed 's/\^M//g' > deploy-logs.txt
RUN cp .brownie/packages/Uniswap/uniswap-v2-core@1.0.1/build/contracts/* /build/contracts
RUN python3 integration/blockscout/blockscout.py

FROM forestfriends/blockscout:postgres
COPY --from=builder /var/lib/dispersion/contracts.sql /docker-entrypoint-initdb.d/1-contracts.sql