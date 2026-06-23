resource "google_storage_bucket" "media" {
  name          = "${var.project_id}-multiserve-media"
  location      = var.region
  force_destroy = false

  uniform_bucket_level_access = true

  versioning {
    enabled = true
  }

  lifecycle_rule {
    condition {
      age = 365
    }
    action {
      type          = "SetStorageClass"
      storage_class = "NEARLINE"
    }
  }

  cors {
    origin          = ["*"]
    method          = ["GET", "HEAD", "PUT", "POST"]
    response_header = ["Content-Type", "Authorization"]
    max_age_seconds = 3600
  }
}

resource "google_storage_bucket_iam_member" "gke_media_admin" {
  bucket = google_storage_bucket.media.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${google_service_account.gke_sa.email}"
}

resource "google_storage_bucket" "static" {
  name          = "${var.project_id}-multiserve-static"
  location      = var.region
  force_destroy = false

  uniform_bucket_level_access = true

  website {
    main_page_suffix = "index.html"
  }
}

resource "google_storage_bucket_iam_member" "static_public_reader" {
  bucket = google_storage_bucket.static.name
  role   = "roles/storage.objectViewer"
  member = "allUsers"
}
