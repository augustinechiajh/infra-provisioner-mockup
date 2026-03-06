from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import subprocess
import os

app = FastAPI(
    title="Infra Provisioner",
    description="Self-service infrastructure provisioning API — like a mini Morpheus",
    version="1.0.0"
)

# --- Request model ---
# This defines what the user sends in the POST request body
class ProvisionRequest(BaseModel):
    resource_type: str   # e.g. "s3_bucket" or "ec2_instance"
    name: str            # e.g. "my-bucket" or "my-server"
    environment: str     # e.g. "dev", "staging"

# --- Response model ---
class ProvisionResponse(BaseModel):
    status: str
    message: str
    resource_type: str
    name: str

# --- Health check endpoint ---
# Always good practice to have one — used by load balancers and monitoring tools
@app.get("/health")
def health_check():
    return {"status": "healthy"}

# --- Main provisioning endpoint ---
@app.post("/provision", response_model=ProvisionResponse)
def provision_resource(request: ProvisionRequest):
    """
    Accepts a provisioning request and triggers Terraform to create the resource.
    
    This is the core of what platforms like Morpheus do:
    user submits a request via UI/API -> backend runs Terraform -> infra gets created
    """

    # Validate resource type
    supported_resources = ["s3_bucket", "ec2_instance"]
    if request.resource_type not in supported_resources:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported resource type: {request.resource_type}. Supported: {supported_resources}"
        )

    # Determine which Terraform module to use based on resource type
    module_path = f"./terraform/modules/{request.resource_type.replace('_', '/')}"
    # e.g. s3_bucket -> terraform/modules/s3

    # Set Terraform variables from the request
    env_vars = os.environ.copy()
    env_vars["TF_VAR_name"] = request.name
    env_vars["TF_VAR_environment"] = request.environment

    try:
        # Run terraform init
        subprocess.run(
            ["terraform", "init"],
            cwd=module_path,
            env=env_vars,
            check=True,
            capture_output=True
        )

        # Run terraform apply
        subprocess.run(
            ["terraform", "apply", "-auto-approve"],
            cwd=module_path,
            env=env_vars,
            check=True,
            capture_output=True
        )

        return ProvisionResponse(
            status="success",
            message=f"Successfully provisioned {request.resource_type} named '{request.name}'",
            resource_type=request.resource_type,
            name=request.name
        )

    except subprocess.CalledProcessError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Terraform failed: {e.stderr.decode()}"
        )
