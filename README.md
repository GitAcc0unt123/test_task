## Run tests
```shell
docker compose -f docker-compose.test.yml up --abort-on-container-exit && docker compose -f docker-compose.test.yml down
```

## Run application
```shell
docker compose -f docker-compose.run.yml up
```
