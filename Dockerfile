FROM forestfriends/ganache-brownie as builder
WORKDIR /var/lib/dispersion

# PRE-INSTALL COMPILERS (FOR CACHE)
RUN mkdir -p /root/.vvm && cd /root/.vvm && wget https://github.com/vyperlang/vyper/releases/download/v0.1.0-beta.16/vyper.0.1.0-beta.16+commit.5e4a94a.linux -O vyper-0.1.0-beta.16 && chmod +x vyper-0.1.0-beta.16
RUN mkdir -p /root/.vvm && cd /root/.vvm && wget https://github.com/vyperlang/vyper/releases/download/v0.1.0-beta.17/vyper.0.1.0-beta.17+commit.0671b7b.linux -O vyper-0.1.0-beta.17 && chmod +x vyper-0.1.0-beta.17
RUN mkdir -p /root/.vvm && cd /root/.vvm && wget https://github.com/vyperlang/vyper/releases/download/v0.2.4/vyper.0.2.4+commit.7949850.linux -O vyper-0.2.4 && chmod +x vyper-0.2.4
RUN mkdir -p /root/.vvm && cd /root/.vvm && wget https://github.com/vyperlang/vyper/releases/download/v0.2.5/vyper.0.2.5+commit.a0c561c.linux -O vyper-0.2.5 && chmod +x vyper-0.2.5
RUN mkdir -p /root/.vvm && cd /root/.vvm && wget https://github.com/vyperlang/vyper/releases/download/v0.2.7/vyper.0.2.7+commit.0b3f3b3.linux -O vyper-0.2.7 && chmod +x vyper-0.2.7
RUN mkdir -p /root/.solcx && cd /root/.solcx && wget https://solc-bin.ethereum.org/linux-amd64/solc-linux-amd64-v0.5.17+commit.d19bba13 -O solc-v0.5.17 && chmod +x solc-v0.5.17
RUN mkdir -p /root/.solcx && cd /root/.solcx && wget https://solc-bin.ethereum.org/linux-amd64/solc-linux-amd64-v0.5.16+commit.9c3226ce -O solc-v0.5.16 && chmod +x solc-v0.5.16
# COMPILE
COPY interfaces interfaces
COPY contracts contracts
ADD brownie-config.yaml brownie-config.yaml
COPY scripts scripts
RUN ganache-cli --db /var/lib/dispersion/db -m "abstract render give egg now oxygen wisdom extend strategy link risk insane" > node-logs.txt & sleep 5 & brownie run development deploy | sed 's/\x1B\[[0-9;]\{1,\}[A-Za-z]//g' | sed 's/\^M//g' > deploy-logs.txt && cat deploy-logs.txt
# INTEGRATION
RUN cp /root/.brownie/packages/Uniswap/uniswap-v2-core@1.0.1/build/contracts/* build/contracts
RUN cp /root/.brownie/packages/curvefi/curve-contract@1.0/build/contracts/* build/contracts
RUN cp -f /root/.brownie/packages/curvefi/curve-dao-contracts@1.1.0/build/contracts/* build/contracts
COPY integration integration
RUN python3 integration/blockscout/blockscout.py
RUN cat contracts.sql

EXPOSE 8545
CMD [ "ganache-cli", "-h", "0.0.0.0", "--db", "/var/lib/dispersion/db", "-m", "abstract render give egg now oxygen wisdom extend strategy link risk insane" ]