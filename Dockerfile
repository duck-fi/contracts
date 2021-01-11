FROM alpine
WORKDIR /var/lib/dispersion
RUN apk add --no-cache musl-dev linux-headers python3-dev gcc py-pip nodejs npm && \
    pip install eth-brownie && npm install -g ganache-cli
ADD contracts contracts
ADD interfaces interfaces
ADD scripts scripts
ADD brownie-config.yaml brownie-config.yaml
ADD requirements.txt requirements.txt
RUN ganache-cli & sleep 5 & brownie run development deploy

EXPOSE 8545
CMD [ "ganache-cli", "-h", "0.0.0.0" ]