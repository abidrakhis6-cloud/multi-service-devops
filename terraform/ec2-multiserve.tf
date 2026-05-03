# ==========================================
# MultiServe - EC2 Instance with Docker
# Déploiement simple sur une instance EC2
# ==========================================

# Security Group pour MultiServe
resource "aws_security_group" "multiserve" {
  name_prefix = "multiserve-sg-"
  description = "Security group for MultiServe application"
  vpc_id      = aws_vpc.main.id

  # HTTP
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTP"
  }

  # HTTPS
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTPS"
  }

  # Application Django (temporaire pour tests)
  ingress {
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Django Development"
  }

  # Grafana
  ingress {
    from_port   = 3001
    to_port     = 3001
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Grafana Monitoring"
  }

  # SSH
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # À restreindre à ton IP perso en prod!
    description = "SSH Access"
  }

  # Sortie complète
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project_name}-sg-${var.environment}"
  }
}

# AMI Ubuntu 22.04 LTS
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"]  # Canonical

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-22.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

# Script d'initialisation (user-data)
locals {
  user_data = <<-EOF
#!/bin/bash
set -e

# Mise à jour
apt-get update
apt-get upgrade -y

# Installation Docker
curl -fsSL https://get.docker.com | sh
usermod -aG docker ubuntu
systemctl enable docker
systemctl start docker

# Installation Docker Compose
curl -L "https://github.com/docker/compose/releases/download/v2.23.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
ln -sf /usr/local/bin/docker-compose /usr/bin/docker-compose

# Création répertoire application
mkdir -p /opt/multiserve
cd /opt/multiserve

# Clone du repository
git clone https://github.com/abidrakhis6-cloud/multi-service-devops.git .

# Fichier .env de base
 cat > .env << 'ENVFILE'
DEBUG=False
SECRET_KEY=$(openssl rand -base64 50 | tr -d '\n')
ALLOWED_HOSTS=13.49.183.244,localhost,127.0.0.1,multi-serve.fr,www.multi-serve.fr
FRONTEND_URL=http://13.49.183.244:8000

# Database SQLite pour test rapide (à remplacer par RDS en prod)
DATABASE_URL=sqlite:///db.sqlite3

# Redis local
REDIS_URL=redis://localhost:6379/0
REDIS_PASSWORD=redislocal123

# TODO: Configurer ces variables manuellement
SENDGRID_API_KEY=
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_PHONE_NUMBER=
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
FACEBOOK_APP_ID=
FACEBOOK_APP_SECRET=
ENVFILE

# Lancement de l'application (mode simple sans nginx pour test)
docker run -d --name redis -p 6379:6379 redis:7-alpine redis-server --requirepass redislocal123

# Build et run
docker build -t multiserve .
docker run -d \
  --name multiserve \
  -p 8000:8000 \
  -v /opt/multiserve:/app \
  -e DJANGO_SETTINGS_MODULE=config.settings \
  -e DATABASE_URL=sqlite:///db.sqlite3 \
  -e REDIS_URL=redis://host.docker.internal:6379/0 \
  multiserve \
  sh -c "python manage.py migrate && python manage.py collectstatic --noinput && gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 2"

# Health check script
cat > /usr/local/bin/health-check.sh << 'HEALTH'
#!/bin/bash
curl -f http://localhost:8000/health/ || systemctl restart docker
HEALTH
chmod +x /usr/local/bin/health-check.sh

# Cron pour health check
echo "*/5 * * * * root /usr/local/bin/health-check.sh" > /etc/cron.d/multiserve-health

# Message de fin
echo "========================================" >> /var/log/user-data.log
echo "MultiServe déployé sur IP: $(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)" >> /var/log/user-data.log
echo "Accès: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):8000" >> /var/log/user-data.log
echo "========================================" >> /var/log/user-data.log
EOF
}

# Instance EC2 MultiServe
resource "aws_instance" "multiserve" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = "t3.small"  # 2 vCPU, 2GB RAM - suffisant pour démarrer

  subnet_id                   = aws_subnet.public[0].id
  vpc_security_group_ids      = [aws_security_group.multiserve.id]
  associate_public_ip_address = true
  key_name                    = aws_key_pair.multiserve.key_name

  user_data = local.user_data
  user_data_replace_on_change = true

  root_block_device {
    volume_size = 20  # GB
    volume_type = "gp3"
    encrypted   = true
  }

  tags = {
    Name = "${var.project_name}-ec2-${var.environment}"
  }
}

# Clé SSH
resource "aws_key_pair" "multiserve" {
  key_name   = "${var.project_name}-key-${var.environment}"
  public_key = file("~/.ssh/id_rsa.pub")  # Doit exister, sinon créer avec ssh-keygen
}

# Output des informations
output "multiserve_public_ip" {
  description = "IP publique de l'instance MultiServe"
  value       = aws_instance.multiserve.public_ip
}

output "multiserve_public_dns" {
  description = "DNS public de l'instance"
  value       = aws_instance.multiserve.public_dns
}

output "multiserve_url" {
  description = "URL d'accès à l'application"
  value       = "http://${aws_instance.multiserve.public_ip}:8000"
}

output "ssh_command" {
  description = "Commande pour se connecter en SSH"
  value       = "ssh -i ~/.ssh/id_rsa ubuntu@${aws_instance.multiserve.public_ip}"
}
