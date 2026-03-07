#!/usr/bin/env python3
"""
Test script to verify AWS Bedrock connectivity and configuration
"""
import os
import sys
import boto3
import json

# Get AWS credentials from environment variables
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-1")

if not AWS_ACCESS_KEY_ID or not AWS_SECRET_ACCESS_KEY:
    print("ERROR: AWS credentials not found in environment variables")
    print("Please set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY")
    sys.exit(1)

print("=" * 60)
print("AWS Bedrock Connection Test")
print("=" * 60)
print()

# Test 1: Check credentials
print("[1/4] Testing AWS credentials...")
try:
    sts_client = boto3.client(
        'sts',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION
    )
    identity = sts_client.get_caller_identity()
    print(f"✅ Credentials valid")
    print(f"    Account: {identity['Account']}")
    print(f"    User: {identity['Arn']}")
except Exception as e:
    print(f"❌ Credentials test failed: {e}")
    sys.exit(1)

print()

# Test 2: List available Bedrock models
print("[2/4] Checking Bedrock model access...")
try:
    bedrock_client = boto3.client(
        'bedrock',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION
    )
    
    models = bedrock_client.list_foundation_models()
    claude_models = [m for m in models['modelSummaries'] if 'claude-3-haiku' in m['modelId']]
    
    if claude_models:
        print(f"✅ Bedrock access granted")
        print(f"    Found {len(claude_models)} Claude 3 Haiku models:")
        for model in claude_models:
            print(f"    - {model['modelId']}")
    else:
        print("❌ No Claude 3 Haiku models found")
        print("    Please enable model access in AWS Console → Bedrock → Model access")
        sys.exit(1)
except Exception as e:
    print(f"❌ Bedrock access test failed: {e}")
    sys.exit(1)

print()

# Test 3: Test Bedrock Runtime
print("[3/4] Testing Bedrock Runtime API...")
try:
    bedrock_runtime = boto3.client(
        'bedrock-runtime',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION
    )
    print("✅ Bedrock Runtime client created successfully")
except Exception as e:
    print(f"❌ Bedrock Runtime test failed: {e}")
    sys.exit(1)

print()

# Test 4: Make a test API call
print("[4/4] Making test API call to Claude 3 Haiku...")
try:
    model_id = "anthropic.claude-3-haiku-20240307-v1:0"
    
    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 100,
        "temperature": 0.7,
        "messages": [
            {
                "role": "user",
                "content": "Say 'Hello from Bedrock!' in one sentence."
            }
        ]
    }
    
    response = bedrock_runtime.invoke_model(
        modelId=model_id,
        body=json.dumps(body)
    )
    
    response_body = json.loads(response.get("body").read())
    response_text = response_body.get("content", [{}])[0].get("text", "")
    
    print(f"✅ API call successful!")
    print(f"    Model: {model_id}")
    print(f"    Response: {response_text}")
    
except Exception as e:
    print(f"❌ API call failed: {e}")
    print()
    print("Common issues:")
    print("  1. Model access not enabled in AWS Console")
    print("  2. IAM permissions missing (AmazonBedrockFullAccess)")
    print("  3. Wrong region (should be us-east-1)")
    print("  4. Model ID incorrect")
    sys.exit(1)

print()
print("=" * 60)
print("✅ All tests passed! Bedrock is configured correctly.")
print("=" * 60)
