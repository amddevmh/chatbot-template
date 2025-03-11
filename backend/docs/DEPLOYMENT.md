# Deployment Guide

This guide explains how to deploy the FastAPI backend using GitHub Actions CI/CD pipelines.

## Deployment Strategy

The project uses a two-part GitHub Actions workflow strategy:

1. **CI Workflow** (`.github/workflows/ci.yml`): Handles testing and building
2. **Deployment Workflow** (platform-specific): Handles the actual deployment

This separation provides several benefits:
- Keeps the codebase cloud provider agnostic
- Makes it easier to switch deployment platforms
- Separates concerns between testing/building and deployment

## Available Deployment Workflows

### Railway Deployment (`.github/workflows/deploy-railway.yml`)

This workflow deploys the application to [Railway](https://railway.app/), a modern PaaS platform.

#### Prerequisites:

1. Create a Railway account and project
2. Generate a Railway API token:
   - Go to Railway dashboard → Settings → Tokens
   - Create a new token with appropriate permissions
3. Add the token to GitHub repository secrets:
   - Go to your GitHub repository → Settings → Secrets and variables → Actions
   - Create a new repository secret named `RAILWAY_TOKEN` with your Railway token

#### How it works:

1. The workflow runs after the CI workflow completes successfully
2. It installs the Railway CLI
3. It deploys the application to Railway using `railway up`

### Generic Deployment Template (`.github/workflows/deploy.yml`)

This is a template file that can be customized for any cloud provider. It provides a starting point with the basic structure needed for deployment.

## Setting Up a New Deployment Target

To deploy to a different platform:

1. Create a new workflow file (e.g., `.github/workflows/deploy-aws.yml`)
2. Use the generic template as a starting point
3. Customize the steps for your specific cloud provider
4. Add any necessary secrets to your GitHub repository

## Required Secrets and Environment Variables

### GitHub Secrets for CI/CD

Add these secrets to your GitHub repository (Settings → Secrets and variables → Actions):

1. **MongoDB Atlas Connection**:
   - `MONGODB_URI`: Your MongoDB Atlas connection string
   - `MONGODB_DATABASE`: Your database name

2. **Authentication**:
   - `JWT_SECRET_KEY`: Secret key for JWT token generation/validation

3. **Deployment Platform**:
   - `RAILWAY_TOKEN`: Your Railway API token (for Railway deployment)

### Environment Variables for Deployment

Configure these in your deployment platform (e.g., Railway):

- **MongoDB Connection**: Same `MONGODB_URI` and `MONGODB_DATABASE` as above
- **JWT Settings**: Same `JWT_SECRET_KEY` as above
- **Environment**: Set `ENVIRONMENT=production` for production deployments
- **Auth Bypass**: Set `AUTH_BYPASS_ENABLED=false` for production

The CI workflow uses the GitHub secrets for testing, while the deployed application uses the environment variables configured in your deployment platform.

## Manual Deployment

You can also trigger deployments manually:

1. Go to your GitHub repository → Actions
2. Select the deployment workflow you want to run
3. Click "Run workflow"
4. Select the branch to deploy
5. Click "Run workflow"

This is useful for deploying specific branches or re-running deployments.
