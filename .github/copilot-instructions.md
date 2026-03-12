# Infra Provisioner — Copilot Instructions

## Project Overview

A self-service infrastructure provisioning API. Users POST to `/provision` with a resource type and name; the FastAPI app triggers Terraform to create the resource against LocalStack (local AWS simulator). No real AWS account needed.

**Stack:** FastAPI · Terraform · LocalStack · Docker Compose · GitHub Actions

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

## Key Files

| Path | Purpose |
|------|---------|
| `app/main.py` | FastAPI app — all API logic lives here |
| `terraform/modules/s3/` | S3 bucket Terraform module |
| `terraform/modules/ec2/` | EC2 instance Terraform module |
| `tests/test_api.py` | API unit tests (no Terraform) |
| `docker-compose.yml` | Runs LocalStack + API together |
| `.github/workflows/ci.yml` | CI: runs pytest + terraform validate |

## Coding Conventions

### Adding a New Resource Type

Every resource type maps to one Terraform module. Follow this pattern:

1. **Create the module** at `terraform/modules/{type}/`:
   - `main.tf` — resource definition using `var.environment` and `var.name`
   - `variables.tf` — declare `name` and `environment` (passed via `TF_VAR_*`)
   - `outputs.tf` — optional, output the resource identifier
   - `provider.tf` — AWS provider pointed at LocalStack (`http://localstack:4566`)

2. **Register it in `app/main.py`**:
   - Add the string key to `supported_resources` list
   - Add the path to `module_map`

3. **Add a test** in `tests/test_api.py` (at minimum: valid request returns 200, unsupported type returns 400).

### Resource Naming

All resources are named `{environment}-{name}` inside Terraform (e.g. `dev-my-bucket`). Enforce this in each module's `main.tf`.

### Terraform Provider Pattern

All modules use LocalStack — copy this provider config:

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
    # add your service endpoint here
  }
}
```

### Tests

Tests use FastAPI's `TestClient` — no Docker or real Terraform required. Test HTTP behaviour only (status codes, response shapes, validation errors). Do not write tests that invoke real Terraform or LocalStack.

## Things to Avoid

- Do not suggest real AWS credentials — this project uses LocalStack only (`access_key = "test"`)
- Do not suggest running `terraform apply` outside Docker — LocalStack is only reachable inside the compose network
- Do not suggest committing `.terraform/` directories or `terraform.tfstate*` files
- Do not use `subprocess` for anything other than Terraform — use FastAPI/Python libraries for everything else
