# terraform/terraform.tfvars

# AWS Configuration
aws_region      = "eu-west-3"
environment     = "production"
project_name    = "multiserve"

# VPC Configuration
vpc_cidr                    = "10.0.0.0/16"
availability_zones_count    = 2
enable_nat_gateway          = true

# EKS Configuration
eks_version                 = "1.28"
node_instance_types         = ["t3.medium"]
node_desired_size           = 3
node_min_size               = 2
node_max_size               = 10
node_capacity_type          = "ON_DEMAND"

# Database Configuration
db_instance_class           = "db.t3.micro"
db_allocated_storage        = 20
db_max_allocated_storage    = 100
db_name                     = "multiserve"
db_username                 = "admin"
db_password                 = "Multiserve2024!"
db_multi_az                 = false
db_backup_retention         = 0
db_deletion_protection      = false

# Redis Configuration
redis_node_type             = "cache.t3.micro"

# Security
allowed_public_cidrs        = ["0.0.0.0/0"]

# SSH Key (optionnel)
ssh_key_name                = ""

# ACM Certificate (optionnel - pour HTTPS)
acm_certificate_arn         = ""
