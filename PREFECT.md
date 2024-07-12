
# Prefect

used prefect commands:-
- ```prefect work-pool create --type process local-pool```
- ```prefect worker start --pool local-pool```
- ```prefect deploy --all```
- ```prefect deployment run 'train-simple-flow/simple-model-training'```

## Connect to prefect server

```bash
prefect config set PREFECT_API_URL="http://localhost:4200/api"
```

## To deploy prefect flows

all the deployment flows are mentioned in the ```prefect.yaml``` file

### To deploy all
```bash
prefect deploy --all
```
### To run deployed flow

e.g.,
```bash
prefect deployment run 'train-simple-flow/simple-model-training'
```
we can also run using prefect UI
