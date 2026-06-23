variable "project_id" {
  description = "ID du projet GCP (ex: multiserve-prod-123456)"
  type        = string
}

variable "region" {
  description = "Region GCP"
  type        = string
  default     = "europe-west1"
}

variable "zone" {
  description = "Zone GCP principale"
  type        = string
  default     = "europe-west1-b"
}

variable "environment" {
  description = "Nom de l'environnement"
  type        = string
  default     = "production"
}

variable "db_name" {
  description = "Nom de la base de données PostgreSQL"
  type        = string
  default     = "multiserve"
}

variable "db_user" {
  description = "Utilisateur PostgreSQL"
  type        = string
  default     = "admin"
}

variable "db_password" {
  description = "Mot de passe PostgreSQL (sensible)"
  type        = string
  sensitive   = true
}

variable "gke_node_count" {
  description = "Nombre de noeuds GKE par zone"
  type        = number
  default     = 2
}

variable "gke_machine_type" {
  description = "Type de machine GKE"
  type        = string
  default     = "e2-standard-2"
}

variable "gke_disk_size_gb" {
  description = "Taille disque des noeuds GKE (Go)"
  type        = number
  default     = 50
}
