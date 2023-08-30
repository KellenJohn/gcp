#!/bin/bash
# method1 
# gcloud functions deploy demo --entry-point hello_world --runtime python39 --trigger-http --allow-unauthenticated

# method 2
gcloud functions deploy demo2 \
  --entry-point hello_world \
  --runtime python39 \
  --trigger-http \
  --allow-unauthenticated \
  --region us-central1 \
  --max-instances 3
  
# dont workable  
#  --set-env-vars FUNCTION_MEMORY_MB=128,FUNCTION_CPU=0.0083 \
