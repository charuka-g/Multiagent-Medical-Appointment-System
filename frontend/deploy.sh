#!/bin/bash

# Frontend Deployment Script for AWS S3
# Usage: ./deploy.sh [bucket-name] [cloudfront-distribution-id]

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
BUCKET_NAME="${1:-your-s3-bucket-name}"
CLOUDFRONT_DISTRIBUTION_ID="${2:-}"

echo -e "${GREEN}=== Frontend Deployment to AWS S3 ===${NC}\n"

# Check if .env.production exists
if [ ! -f ".env.production" ]; then
    echo -e "${YELLOW}Warning: .env.production not found${NC}"
    echo "Please create .env.production with NEXT_PUBLIC_BACKEND_URL"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo -e "${GREEN}✓ Found .env.production${NC}"
fi

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo -e "${RED}Error: AWS CLI is not installed${NC}"
    echo "Please install AWS CLI: https://aws.amazon.com/cli/"
    exit 1
fi

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}Installing dependencies...${NC}"
    npm install
fi

# Build the application
echo -e "\n${GREEN}Building application...${NC}"
npm run build

if [ ! -d "out" ]; then
    echo -e "${RED}Error: Build failed - 'out' directory not found${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Build successful${NC}"

# Upload to S3
echo -e "\n${GREEN}Uploading to S3 bucket: ${BUCKET_NAME}...${NC}"
aws s3 sync out s3://$BUCKET_NAME --delete --exclude ".DS_Store"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Upload successful${NC}"
else
    echo -e "${RED}Error: Upload failed${NC}"
    exit 1
fi

# Invalidate CloudFront cache if distribution ID is provided
if [ ! -z "$CLOUDFRONT_DISTRIBUTION_ID" ]; then
    echo -e "\n${GREEN}Invalidating CloudFront cache...${NC}"
    aws cloudfront create-invalidation \
        --distribution-id $CLOUDFRONT_DISTRIBUTION_ID \
        --paths "/*" \
        --output json > /dev/null
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Cache invalidation initiated${NC}"
    else
        echo -e "${YELLOW}Warning: Cache invalidation failed${NC}"
    fi
else
    echo -e "${YELLOW}Note: CloudFront distribution ID not provided, skipping cache invalidation${NC}"
fi

echo -e "\n${GREEN}=== Deployment Complete! ===${NC}"
echo -e "Your frontend is now live on S3: ${BUCKET_NAME}"
if [ ! -z "$CLOUDFRONT_DISTRIBUTION_ID" ]; then
    echo -e "CloudFront distribution: ${CLOUDFRONT_DISTRIBUTION_ID}"
fi

