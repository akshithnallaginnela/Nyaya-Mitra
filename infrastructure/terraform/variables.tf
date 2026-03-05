# ============================================
# Nyaya Mitra — Terraform Variables
# ============================================

# ─── General ───
variable "project_name" {
  description = "Project name used for resource naming"
  type        = string
  default     = "nyaya-mitra"
}

variable "environment" {
  description = "Environment name (development, staging, production)"
  type        = string
  default     = "production"

  validation {
    condition     = contains(["development", "staging", "production"], var.environment)
    error_message = "Environment must be development, staging, or production."
  }
}

variable "aws_region" {
  description = "AWS region for deployment"
  type        = string
  default     = "ap-south-1" # Mumbai — closest to Indian users
}

variable "domain_name" {
  description = "Domain name for the application"
  type        = string
  default     = "nyayamitra.com"
}

# ─── Database (RDS) ───
variable "db_instance_class" {
  description = "RDS instance type"
  type        = string
  default     = "db.t3.micro" # Free tier eligible
}

variable "db_name" {
  description = "Database name"
  type        = string
  default     = "nyaya_mitra"
}

variable "db_username" {
  description = "Database master username"
  type        = string
  default     = "nyaya_admin"
  sensitive   = true
}

variable "db_password" {
  description = "Database master password"
  type        = string
  sensitive   = true
}

# ─── ECS (Container Service) ───
variable "ecs_task_cpu" {
  description = "CPU units for ECS task (1024 = 1 vCPU)"
  type        = string
  default     = "1024" # 1 vCPU
}

variable "ecs_task_memory" {
  description = "Memory for ECS task in MiB"
  type        = string
  default     = "4096" # 4 GB (needed for AI model loading)
}

variable "ecs_desired_count" {
  description = "Desired number of ECS tasks"
  type        = number
  default     = 1
}

variable "ecs_max_count" {
  description = "Maximum number of ECS tasks for auto-scaling"
  type        = number
  default     = 4
}

# ─── AI / Ollama ───
variable "ollama_base_url" {
  description = "Ollama API base URL (separate EC2 instance or sidecar)"
  type        = string
  default     = "http://localhost:11434"
}

variable "ollama_model" {
  description = "Ollama model to use"
  type        = string
  default     = "llama3.2:3b"
}

# ─── Security ───
variable "jwt_secret" {
  description = "JWT secret key for authentication"
  type        = string
  sensitive   = true
}

# variable "acm_certificate_arn" {
#   description = "ACM certificate ARN for HTTPS"
#   type        = string
#   default     = ""
# }
