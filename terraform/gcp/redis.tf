resource "google_redis_instance" "cache" {
  name           = "multiserve-redis"
  tier           = "BASIC"
  memory_size_gb = 1
  region         = var.region

  location_id = "${var.region}-b"

  authorized_network = google_compute_network.vpc.id
  connect_mode       = "PRIVATE_SERVICE_ACCESS"

  redis_version = "REDIS_7_0"
  display_name  = "MultiServe Redis Cache"

  auth_enabled            = true
  transit_encryption_mode = "DISABLED"

  redis_configs = {
    maxmemory-policy = "allkeys-lru"
  }

  maintenance_policy {
    weekly_maintenance_window {
      day = "SUNDAY"
      start_time {
        hours   = 2
        minutes = 0
        seconds = 0
        nanos   = 0
      }
    }
  }

  depends_on = [google_service_networking_connection.private_vpc_connection]
}
