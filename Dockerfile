FROM alpine as builder
WORKDIR /var/lib/dispersion
RUN apk add --no-cache musl-dev linux-headers python3-dev gcc py-pip nodejs npm && npm install -g ganache-cli
COPY interfaces interfaces
COPY contracts contracts
COPY scripts scripts
COPY integration integration
ADD brownie-config.yaml requirements.txt ./
RUN pip3 install -r requirements.txt
RUN brownie compile
RUN ganache-cli --db /var/lib/dispersion/db -m "abstract render give egg now oxygen wisdom extend strategy link risk insane" > node-logs.txt & sleep 5 & brownie run development deploy | sed 's/\x1B\[[0-9;]\{1,\}[A-Za-z]//g' > deploy-logs.txt
RUN cat -v deploy-logs.txt | sed 's/\^M//g' > deploy-logs.txt
# RUN cp /root/.brownie/packages/Uniswap/uniswap-v2-core@1.0.1/build/contracts/* build/contracts
RUN cat -v deploy-logs.txt
RUN python3 integration/blockscout/blockscout.py
RUN cat -v contracts.sql

EXPOSE 8545
CMD [ "ganache-cli", "-h", "0.0.0.0", "--db", "/var/lib/dispersion/db", "-m", "abstract render give egg now oxygen wisdom extend strategy link risk insane" ]