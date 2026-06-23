resource "google_compute_network" "vpc" {
  name                    = "multiserve-vpc"
  auto_create_subnetworks = false
  description             = "VPC principal MultiServe"
}

resource "google_compute_subnetwork" "private" {
  name          = "multiserve-private-subnet"
  ip_cidr_range = "10.0.0.0/20"
  region        = var.region
  network       = google_compute_network.vpc.id
  description   = "Sous-réseau privé pour GKE et services"

  secondary_ip_range {
    range_name    = "k8s-pods"
    ip_cidr_range = "10.48.0.0/14"
  }

  secondary_ip_range {
    range_name    = "k8s-services"
    ip_cidr_range = "10.52.0.0/20"
  }

  private_ip_google_access = true
}

resource "google_compute_router" "router" {
  name    = "multiserve-router"
  region  = var.region
  network = google_compute_network.vpc.id
}

resource "google_compute_router_nat" "nat" {
  name                               = "multiserve-nat"
  router                             = google_compute_router.router.name
  region                             = var.region
  nat_ip_allocate_option             = "AUTO_ONLY"
  source_subnetwork_ip_ranges_to_nat = "ALL_SUBNETWORKS_ALL_IP_RANGES"

  log_config {
    enable = true
    filter = "ERRORS_ONLY"
  }
}

resource "google_compute_global_address" "private_ip_range" {
  name          = "multiserve-private-ip-range"
  purpose       = "VPC_PEERING"
  address_type  = "INTERNAL"
  prefix_length = 16
  network       = google_compute_network.vpc.id
  description   = "Plage IP privée pour Cloud SQL et Memorystore"
}

resource "google_service_networking_connection" "private_vpc_connection" {
  network                 = google_compute_network.vpc.id
  service                 = "servicenetworking.googleapis.com"
  reserved_peering_ranges = [google_compute_global_address.private_ip_range.name]
}

resource "google_compute_firewall" "allow_internal" {
  name    = "multiserve-allow-internal"
  network = google_compute_network.vpc.name

  allow {
    protocol = "tcp"
    ports    = ["0-65535"]
  }
  allow {
    protocol = "udp"
    ports    = ["0-65535"]
  }
  allow {
    protocol = "icmp"
  }

  source_ranges = ["10.0.0.0/8"]
  description   = "Autorise le trafic interne entre les services"
}

resource "google_compute_firewall" "allow_health_checks" {
  name    = "multiserve-allow-health-checks"
  network = google_compute_network.vpc.name

  allow {
    protocol = "tcp"
    ports    = ["8000", "80", "443"]
  }

  source_ranges = ["35.191.0.0/16", "130.211.0.0/22"]
  description   = "Autorise les health checks Google Load Balancer"
}
