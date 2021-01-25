ARG image
FROM ${image} as builder
FROM forestfriends/blockscout:postgres
COPY --from=builder /var/lib/dispersion/contracts.sql /docker-entrypoint-initdb.d/1-contracts.sql