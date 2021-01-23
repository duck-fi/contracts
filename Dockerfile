FROM alpine as builder
WORKDIR /var/lib/dispersion

# DEPS
RUN apk add --no-cache musl-dev linux-headers python3-dev gcc py-pip nodejs npm && \
    pip install eth-brownie && npm install -g ganache-cli
# COMPILE
COPY interfaces interfaces
COPY contracts contracts
RUN brownie compile
COPY scripts scripts
ADD brownie-config.yaml brownie-config.yaml
RUN ganache-cli --db /var/lib/dispersion/db -m "abstract render give egg now oxygen wisdom extend strategy link risk insane" > node-logs.txt & sleep 5 & brownie run development deploy > deploy-logs.txt
# INTEGRATION
RUN cp /root/.brownie/packages/Uniswap/uniswap-v2-core@1.0.1/build/contracts/* build/contracts
RUN cat -v deploy-logs.txt | sed 's/\x1B\[[0-9;]\{1,\}[A-Za-z]//g' | sed 's/\^M//g' > deploy-logs.txt
RUN cat -v deploy-logs.txt
COPY integration integration
RUN python3 integration/blockscout/blockscout.py
RUN cat -v contracts.sql

EXPOSE 8545
CMD [ "ganache-cli", "-h", "0.0.0.0", "--db", "/var/lib/dispersion/db", "-m", "abstract render give egg now oxygen wisdom extend strategy link risk insane" ]