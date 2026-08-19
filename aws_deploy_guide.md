# ☁️ AWS Cloud Deployment Guide for CareerOS

This guide provides 2 simple, production-grade deployment options for running **CareerOS** on AWS Cloud.

---

## 🎯 Option 1: AWS App Runner (Fastest & Easiest — 5 Minutes)

AWS App Runner automatically builds and deploys your containerized CareerOS application with a secure HTTPS URL.

### Step 1: Push Container to AWS ECR (Elastic Container Registry)

Open your Mac terminal:

```bash
# 1. Log in to your AWS account CLI
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <AWS_ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com

# 2. Create ECR repository
aws ecr create-repository --repository-name career-os

# 3. Build Docker image locally
docker build -t career-os .

# 4. Tag & Push Docker image to AWS ECR
docker tag career-os:latest <AWS_ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/career-os:latest
docker push <AWS_ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/career-os:latest
```

### Step 2: Create AWS App Runner Service

1. Open **AWS App Runner Console** $\rightarrow$ Click **Create Service**.
2. Select **Container Registry** $\rightarrow$ Choose **Amazon ECR**.
3. Select your repository `career-os:latest`.
4. Under **Environment Variables**, configure your encrypted credentials:
   - `NVIDIA_API_KEY`
   - `RAPIDAPI_KEY`
   - `SERPAPI_KEY`
   - `FIRECRAWL_API_KEY`
5. Click **Create & Deploy**!

In **3 minutes**, AWS will issue your live HTTPS production URL:  
👉 `https://<unique-id>.us-east-1.awsapprunner.com`

---

## 🏗️ Option 2: AWS ECS (Elastic Container Service) + AWS Fargate

For enterprise deployments requiring dedicated VPC isolation and custom domain management.

1. **Create ECS Cluster**: Choose **AWS Fargate (Serverless)**.
2. **Register Task Definition**:
   - Container Image: `<AWS_ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/career-os:latest`
   - Memory: `2 GB` | CPU: `1 vCPU`
   - Port Mapping: `8501`
3. **Configure AWS Secrets Manager**:
   - Store API keys inside **AWS Secrets Manager** (`kms/aws/secretsmanager`).
   - Reference secrets dynamically inside the ECS Task Definition environment block.
4. **Launch ECS Service**: Attach an **Application Load Balancer (ALB)** with an SSL certificate.

---

## 🔒 Security Best Practices

1. **AWS KMS AES-256 Encryption**: All secrets stored in AWS Secrets Manager are encrypted at rest using AES-256.
2. **Zero Hardcoded Keys**: No API keys are embedded inside Docker images or source code.
3. **Isolated Container Execution**: Playwright Firefox runs inside an isolated, non-root Linux container environment.
