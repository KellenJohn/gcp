### Create Docker repository in Artifact Registry

```bash
gcloud artifacts repositories create quickstart-docker-repo --repository-format=docker \
    --location=us-west2 --description="Docker repository"
```

### Build the Docker Image
```bash
gcloud builds submit --region=us-west2 --tag us-west2-docker.pkg.dev/project-id/quickstart-docker-repo/quickstart-image:tag1
```
