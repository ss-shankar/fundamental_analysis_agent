
import boto3
from botocore.exceptions import ClientError, NoCredentialsError

# Change this to your AWS region
REGION = "us-east-1"

try:
    # Create a Bedrock client using your AWS CLI credentials
    client = boto3.client(
        service_name="bedrock",
        region_name=REGION
    )

    # Test connectivity and permissions
    response = client.list_foundation_models()

    print("✅ AWS Bedrock connection successful!")
    print(f"Region: {REGION}")
    print(f"Available foundation models: {len(response['modelSummaries'])}")

    for model in response["modelSummaries"][:5]:
        print(f"- {model['modelId']}")

except NoCredentialsError:
    print("❌ AWS credentials not found.")
    print("Run: aws configure")

except ClientError as e:
    print("❌ AWS Bedrock API error:")
    print(e.response["Error"]["Code"])
    print(e.response["Error"]["Message"])

except Exception as e:
    print(f"❌ Unexpected error: {e}")
