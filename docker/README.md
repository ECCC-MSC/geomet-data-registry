# geomet-data-registry Docker setup

Development environment using Docker

## Docker

To start up just geomet-data-registry without any services:

```bash
# build image
make build

# run
make run

# login to a bash session
make login

# stop
make stop
```

## Docker Compose


```bash
# run GDR with embedded services:
docker network create geomet-data-registry-network
docker-compose up -d

# run GDR without services (i.e. ES and Redis already exist)
docker-compose -f docker-compose-nightly.yml up -d
```
