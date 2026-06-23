output "gke_cluster_name" {
  description = "Nom du cluster GKE"
  value       = google_container_cluster.primary.name
}

output "gke_cluster_endpoint" {
  description = "Endpoint du cluster GKE"
  value       = google_container_cluster.primary.endpoint
  sensitive   = true
}

output "artifact_registry_url" {
  description = "URL de l'Artifact Registry (utiliser dans le CI/CD)"
  value       = "${var.region}-docker.pkg.dev/${var.project_id}/multiserve"
}

output "cloud_sql_instance_name" {
  description = "Nom de l'instance Cloud SQL"
  value       = google_sql_database_instance.postgres.name
}

output "cloud_sql_connection_name" {
  description = "Connection name Cloud SQL (pour Cloud SQL Proxy)"
  value       = google_sql_database_instance.postgres.connection_name
}

output "cloud_sql_private_ip" {
  description = "IP privée Cloud SQL"
  value       = google_sql_database_instance.postgres.private_ip_address
}

output "redis_host" {
  description = "Host Redis Memorystore"
  value       = google_redis_instance.cache.host
}

output "redis_port" {
  description = "Port Redis Memorystore"
  value       = google_redis_instance.cache.port
}

output "redis_auth_string" {
  description = "Token d'authentification Redis"
  value       = google_redis_instance.cache.auth_string
  sensitive   = true
}

output "media_bucket_name" {
  description = "Nom du bucket GCS media"
  value       = google_storage_bucket.media.name
}

output "static_bucket_name" {
  description = "Nom du bucket GCS static"
  value       = google_storage_bucket.static.name
}

output "cicd_service_account_email" {
  description = "Email du Service Account CI/CD (à exporter en JSON pour GitHub Secrets)"
  value       = google_service_account.cicd_sa.email
}

output "gke_region" {
  description = "Région GKE"
  value       = var.region
}

output "project_id" {
  description = "ID du projet GCP"
  value       = var.project_id
}
