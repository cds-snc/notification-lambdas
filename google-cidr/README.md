# Google CIDR Lambda
Retrieves the public Google service Classless Inter-Domain Routing (CIDR) ranges and updates an AWS managed prefix list.  This prefix list can then be used to create security group rules that allow services to access Google.

The source of the CIDR ranges are the following two JSON files:

- `services`: https://www.gstatic.com/ipranges/goog.json
- `cloud`: https://www.gstatic.com/ipranges/cloud.json

The final list of CIDR ranges is the result of `services - cloud` CIDR ranges.

## Deployment
1. Create a Lambda function using the Docker image built from this directory.
1. Create a managed prefix list that this Lambda function will update.
1. Create a CloudWatch event rule that triggers the Lambda function once a day.

## Credits
The code in the lambda is adapted from [Google's Cloud CIDR tool](https://github.com/GoogleCloudPlatform/networking-tools-python/tree/main/tools/cidr).