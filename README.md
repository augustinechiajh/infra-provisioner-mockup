# Infra Provisioner

A self-service infrastructure provisioning API.

## What it does

User sends a POST request to `/provision` with a resource type and name.
The API triggers Terraform in the background.
Terraform provisions the resource against LocalStack (free local AWS simulator).

This is conceptually what enterprise platforms do — abstract infrastructure provisioning behind a simple API or UI.

## Architecture

```
User Request (POST /provision)
        |
   FastAPI App
        |
   Terraform Run
        |
   LocalStack (simulated AWS)
        |
   Resource Created (S3, EC2, etc.)
```

## Stack

- **FastAPI** — REST API framework
- **Terraform** — Infrastructure as Code
- **LocalStack** — Free local AWS simulator
- **Docker Compose** — Runs everything together
- **GitHub Actions** — CI/CD pipeline

## Getting Started

### Prerequisites
- Docker Desktop with WSL2 integration enabled
- Git

### Run locally

```bash
# Clone the repo
git clone <your-repo-url>
cd infra-provisioner

# Start LocalStack and the API
docker-compose up

# API is now running at http://localhost:8000
# Interactive docs at http://localhost:8000/docs
```

### Test the API

```bash
# Health check
curl http://localhost:8000/health

# Provision an S3 bucket
curl -X POST http://localhost:8000/provision \
  -H "Content-Type: application/json" \
  -d '{"resource_type": "s3_bucket", "name": "my-bucket", "environment": "dev"}'

# Provision an EC2 instance
curl -X POST http://localhost:8000/provision \
  -H "Content-Type: application/json" \
  -d '{"resource_type": "ec2_instance", "name": "my-server", "environment": "dev"}'
```

### Interactive API docs

FastAPI auto-generates documentation at:
`http://localhost:8000/docs`

This gives you a UI to test the API without curl — useful for demos.

## Project Structure

```
infra-provisioner/
├── app/
│   └── main.py                    # FastAPI application
├── terraform/
│   └── modules/
│       ├── s3/main.tf             # S3 bucket module
│       └── ec2/main.tf            # EC2 instance module
├── tests/
│   └── test_api.py                # API tests
├── .github/
│   └── workflows/
│       └── ci.yml                 # GitHub Actions pipeline
├── docker-compose.yml             # Runs LocalStack + API together
├── Dockerfile                     # Containerises the FastAPI app
└── requirements.txt               # Python dependencies
```

## Extending it

Ideas for extending this project:
- Add more resource types (RDS, Lambda, VPC)
- Add an approval workflow before provisioning
- Add a simple HTML frontend form (like the Backstage self-service form)
- Add a `/deprovision` endpoint to destroy resources
- Store provisioning history in a database
