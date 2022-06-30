## How to run
```
cp env_example .env
```
Provide your credentials to .env file

```bash
docker build -t awscdk_test .

docker run --rm awscdk_test --env-file=.env
```