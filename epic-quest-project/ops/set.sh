# setting environment variables
export PROJECT_ID=esun-cncf
export REGION=asia-east1

# enable relevant apis
gcloud services enable run.googleapis.com \
artifactregistry.googleapis.com compute.googleapis.com cloudbuild.googleapis.com 

# update gcloud with project id and region
gcloud config set project $PROJECT_ID
gcloud config set compute/region $REGION

gcloud artifacts repositories create epic-quest --repository-format="DOCKER" --location=$REGION

