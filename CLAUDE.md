# Infra Provisioner — Claude Instructions

## Project Overview

A self-service infrastructure provisioning API. Users POST to `/provision` with a resource type and name; the FastAPI app triggers Terraform to create the resource against LocalStack (local AWS simulator). No real AWS account needed.

**Stack:** FastAPI · Terraform · LocalStack · Docker Compose · GitHub Actions

## Running Locally

```bash
# Start everything (LocalStack + API)
docker-compose up

# API: http://localhost:8000
# Swagger UI: http://localhost:8000/docs
```

Terraform runs **inside the `api` container** — the `./terraform` directory is mounted as a volume. Do not run `terraform apply` directly on the host.

## Running Tests

Tests use FastAPI's `TestClient` and mock Terraform — no Docker needed.

```bash
pip install -r requirements.txt pytest httpx
pytest tests/ -v
```

Tests live in `tests/test_api.py`. They test HTTP-level behaviour only (status codes, response shapes, validation errors). Do not add tests that invoke real Terraform or LocalStack.

## Architecture

```
POST /provision
     │
 app/main.py          ← FastAPI, validates request, sets TF_VAR_* env vars
     │
 subprocess (terraform init + apply)
     │
 terraform/modules/{s3,ec2}/   ← one module per resource type
     │
 LocalStack :4566      ← simulates AWS S3 / EC2
```

## Adding a New Resource Type

Follow this pattern exactly — every resource type maps to one Terraform module:

1. **Create the module** at `terraform/modules/{type}/`:
   - `main.tf` — resource definition using `var.environment` and `var.name`
   - `variables.tf` — declare `name` and `environment` variables (passed via `TF_VAR_*`)
   - `outputs.tf` — optional, output the resource identifier
   - `provider.tf` — AWS provider pointed at LocalStack (`http://localstack:4566`)

2. **Register it in `app/main.py`**:
   - Add the string key to `supported_resources` list
   - Add the path to `module_map`

3. **Add a test** in `tests/test_api.py` for the new resource type (at minimum: valid request returns 200, invalid name returns 400).

### Resource naming convention

All resources are named `{environment}-{name}` inside Terraform (e.g. `dev-my-bucket`). This is enforced in each module's `main.tf`.

### Provider config pattern (copy from existing modules)

```hcl
provider "aws" {
  region                      = "us-east-1"
  access_key                  = "test"
  secret_key                  = "test"
  skip_credentials_validation = true
  skip_metadata_api_check     = true
  skip_requesting_account_id  = true

  endpoints {
    s3  = "http://localstack:4566"
    ec2 = "http://localstack:4566"
    # add your service here
  }
}
```

## Key Files

| Path | Purpose |
|------|---------|
| `app/main.py` | FastAPI app — all API logic lives here |
| `terraform/modules/s3/` | S3 bucket Terraform module |
| `terraform/modules/ec2/` | EC2 instance Terraform module |
| `tests/test_api.py` | API unit tests (no Terraform) |
| `docker-compose.yml` | Runs LocalStack + API together |
| `.github/workflows/ci.yml` | CI: runs pytest + terraform validate |

## What NOT to Do

- Do not commit `.terraform/` directories or `terraform.tfstate*` files — they are gitignored
- Do not run `terraform apply` outside the Docker container (LocalStack is only reachable inside the compose network)
- Do not add real AWS credentials — this project is LocalStack-only
- Do not call `subprocess` for anything other than Terraform — use FastAPI/Python libraries instead

## Extending This Project (Roadmap Ideas)

- `/deprovision` endpoint — `terraform destroy` the resource
- Provisioning history — store requests + outcomes in SQLite
- Approval workflow — hold request in `pending` state, require a second POST to confirm
- Frontend form — simple HTML page mimicking a Backstage self-service portal
- More resource types — RDS, Lambda, VPC, SQS
