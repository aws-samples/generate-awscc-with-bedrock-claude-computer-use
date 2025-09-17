# Generate AWSCC Documentation with LLM / Agent

This solution will generate example Terraform configuration for the specified AWSCC Terraform provider resource.

The idea behind this project is to automate the research of new AWS resources in AWSCC provider through AWS documentations, and use the knowledge to generate, test and validate Terraform configurations, before publishing it to Terraform registry. You can find example of LLM-generated code example such as  [awscc_apigateway_authorizer](https://registry.terraform.io/providers/hashicorp/awscc/latest/docs/resources/apigateway_authorizer), [awscc_appconfig_configuration_profile](https://registry.terraform.io/providers/hashicorp/awscc/latest/docs/resources/appconfig_configuration_profile), [awscc_m2_environment](https://registry.terraform.io/providers/hashicorp/awscc/latest/docs/resources/m2_environment) and more.

There is two solution in this repository:
* branch [tango](https://github.com/aws-samples/generate-awscc-with-bedrock-claude-computer-use/tree/tango) is the new solution using agentic framework StrandsAgent **recommended**. 
* branch [non-agent](https://github.com/aws-samples/generate-awscc-with-bedrock-claude-computer-use/tree/non-agent) is the original implementation using Anthropic Computer Use + Amazon Bedrock, orchestrated using state-machine.

## Contributing

We hope this solution would inspire you to create similar solution to fit your use-cases. 

Contributions to bug fixes are welcome! Please feel free to submit a Pull Request.

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the [LICENSE](LICENSE) file.
