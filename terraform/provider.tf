# ==========================================
# Terraform Provider Configuration
# ==========================================

terraform {
  required_version = ">= 1.5.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  
  # Backend local (pas de remote state pour l'instant)
  backend "local" {
    path = "terraform.tfstate"
  }
}

# Configuration AWS
provider "aws" {
  region = var.aws_region
  
  default_tags {
    tags = {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "terraform"
    }
  }
}

# Provider pour Stockholm (eu-north-1) où est l'instance
data "aws_caller_identity" "current" {}

data "aws_region" "current" {}
