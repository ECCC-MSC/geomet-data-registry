# geomet-data-registry Docker setup

Development environment using Docker

## Docker

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
docker network create geomet-data-registry-network
docker-compose up -d
```
