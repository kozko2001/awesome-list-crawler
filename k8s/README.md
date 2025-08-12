# Awesome Crawler Kubernetes Deployment

This directory contains Kubernetes manifests to deploy the awesome-crawler as a scheduled job.

## Prerequisites

You'll need to create the AWS S3 credentials secret manually before deploying.

## Setup Instructions

### 1. Create AWS S3 Secret

Create the required secret with your AWS credentials:

```bash
kubectl create secret generic aws-s3-credentials \
  --namespace=awesome-crawler \
  --from-literal=AWS_ACCESS_KEY_ID="your-access-key-id" \
  --from-literal=AWS_SECRET_ACCESS_KEY="your-secret-access-key" \
  --from-literal=AWS_DEFAULT_REGION="us-east-1" \
  --from-literal=S3_BUCKET="awesome-crawler.allocsoc.net"
```

### 2. Deploy the Application

Apply all manifests:

```bash
kubectl apply -f k8s/
```

Or use kustomize:

```bash
kubectl apply -k k8s/
```

## Configuration

- **Schedule**: Runs daily at 00:00 UTC
- **Image**: `harbor.allocsoc.net/awesome-crawler/awesome-crawler:latest`
- **Resources**: 256Mi/512Mi memory, 100m/500m CPU
- **Timeout**: 1 hour active deadline

## Monitoring

Check cronjob status:
```bash
kubectl get cronjobs -n awesome-crawler
kubectl get jobs -n awesome-crawler
kubectl logs -n awesome-crawler job/awesome-crawler-job-<timestamp>
```