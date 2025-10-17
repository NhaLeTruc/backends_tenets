# Docker compose Airflow common permission issue on linux

## Getting Started

```bash
# make sure /opt/airflow/ is in your jurisdiction and of group root (0)
sudo chown -R "1000:0" /opt/airflow/

# make sure your username is in root (0) group
sudo usermod -aG 0 your-username

# run all services including those of profile `pipeline`
docker compose -f airflow-option-four/docker-compose.yaml --profile pipeline up -d
```
