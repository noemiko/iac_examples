https://learn.hashicorp.com/tutorials/terraform/install-cli?in=terraform/aws-get-started
brew tap hashicorp/tap
brew install hashicorp/tap/terraform
terraform -install-autocomplete

terraform apply
How to visualize 
https://medium.com/vmacwrites/tools-to-visualize-your-terraform-plan-d421c6255f9f

https://hieven.github.io/terraform-visual/

or 

terraform graph -type=plan | dot -Tpng > graph.png

inframap generate --connections=false . | dot -Tpng > graph.png