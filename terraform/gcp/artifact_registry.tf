resource "google_artifact_registry_repository" "multiserve" {
  location      = var.region
  repository_id = "multiserve"
  description   = "MultiServe Docker image repository"
  format        = "DOCKER"

  cleanup_policies {
    id     = "keep-last-10"
    action = "KEEP"

    most_recent_versions {
      keep_count = 10
    }
  }

  cleanup_policies {
    id     = "delete-old-untagged"
    action = "DELETE"

    condition {
      tag_state  = "UNTAGGED"
      older_than = "2592000s" # 30 jours
    }
  }
}

resource "google_artifact_registry_repository_iam_member" "gke_reader" {
  project    = var.project_id
  location   = var.region
  repository = google_artifact_registry_repository.multiserve.name
  role       = "roles/artifactregistry.reader"
  member     = "serviceAccount:${google_service_account.gke_sa.email}"
}

resource "google_artifact_registry_repository_iam_member" "cicd_writer" {
  project    = var.project_id
  location   = var.region
  repository = google_artifact_registry_repository.multiserve.name
  role       = "roles/artifactregistry.writer"
  member     = "serviceAccount:${google_service_account.cicd_sa.email}"
}
