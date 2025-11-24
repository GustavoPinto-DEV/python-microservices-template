# Deployment Documentation

This directory contains comprehensive deployment guides and production-ready configuration files for deploying Python microservices templates.

## 📚 Deployment Guides

### [Docker Deployment Guide](guides/DOCKER_DEPLOYMENT.md)
Complete guide for deploying the microservices using Docker with production-optimized configurations.

**Topics covered:**
- Multi-stage Docker builds
- Production Docker Compose orchestration
- Network isolation and security
- Health checks and monitoring
- Resource limits and scaling
- SSL/TLS configuration with Nginx
- Prometheus metrics integration
- Automated backups and rollback

### [Compiled Artifacts Deployment](guides/COMPILED_ARTIFACTS.md)
Advanced deployment strategies using compiled Python artifacts instead of source code.

**Deployment modalities:**
- **Windows Services (NSSM):** Deploy as Windows services with compiled wheels or PyInstaller executables
- **Docker with Wheels:** Multi-stage builds with compiled bytecode for improved security
- **Linux Systemd:** Deploy to Linux servers with systemd units and security hardening

**Benefits:**
- Improved security (no source code exposure)
- Faster startup times
- Smaller deployment packages
- Better performance

### [Docker Integration Summary](guides/DOCKER_INTEGRATION.md)
Executive summary and quick reference for Docker deployment integration.

**Contents:**
- Architectural overview
- Quick start guide
- Service dependencies
- Configuration management
- Monitoring and observability
- Scaling strategies

## 🔧 Production Configuration Files

The [`production-configs/`](production-configs/) directory contains ready-to-use production configuration files:

### Docker Configurations
- **docker-compose.production.yml** - Complete production orchestration with 8+ services
- **Dockerfile.production.template** - Multi-stage build template producing optimized images
- **.dockerignore.production** - Optimized ignore patterns for production builds

### Web Server & Proxy
- **nginx.production.conf** - Production Nginx configuration with:
  - SSL/TLS termination
  - Rate limiting
  - Security headers
  - Gzip compression
  - Reverse proxy setup

### Build & Deployment Tools
- **Makefile.production** - 50+ utility commands for Docker management:
  - `make build` - Build all images
  - `make up` - Start all services
  - `make logs` - View logs
  - `make backup-db` - Backup database
  - `make scale-api N=3` - Scale services
  - `make health` - Check service health

- **setup-docker-production.sh** - Automated setup script for production environment

### Monitoring
- **prometheus.yml.example** - Prometheus metrics configuration for monitoring

## 🚀 Quick Start

### Development Environment
For development, refer to the main [README.md](../../README.md) in the root directory.

### Production Deployment with Docker

1. **Copy and configure production files:**
   ```bash
   cp docs/deployment/production-configs/docker-compose.production.yml ./
   cp docs/deployment/production-configs/.env.production.example .env
   # Edit .env with your production values
   ```

2. **Build and deploy:**
   ```bash
   make build  # Build all images
   make up     # Start all services
   make health # Verify health
   ```

3. **Configure SSL/TLS:**
   ```bash
   # Using Let's Encrypt
   sudo certbot certonly --standalone -d yourdomain.com
   ```

For detailed instructions, see the [Docker Deployment Guide](guides/DOCKER_DEPLOYMENT.md).

### Production Deployment with Compiled Artifacts

For deployments requiring compiled Python artifacts (Windows Services, systemd, etc.), see the [Compiled Artifacts Guide](guides/COMPILED_ARTIFACTS.md).

## 📊 Architecture Overview

### Production Stack
```
┌──────────────────────────────────────────────────┐
│  Load Balancer / Nginx (SSL Termination)       │
└───────────────────┬──────────────────────────────┘
                    │
    ┌───────────────┼───────────────┐
    │               │               │
┌───▼────┐    ┌────▼────┐    ┌────▼─────┐
│ API    │    │ Web App │    │ Workers  │
│ (x3)   │    │ (x2)    │    │ (x2)     │
└───┬────┘    └────┬────┘    └────┬─────┘
    │              │              │
    └──────────────┼──────────────┘
                   │
         ┌─────────▼─────────┐
         │   PostgreSQL      │
         │   (Primary)       │
         └─────────┬─────────┘
                   │
         ┌─────────▼─────────┐
         │   Redis Cache     │
         └───────────────────┘
```

### Monitoring & Observability
- **Prometheus:** Metrics collection
- **Grafana:** Dashboards and visualization
- **Health Checks:** Kubernetes-style probes
- **Centralized Logging:** Structured JSON logs

## 🔒 Security Considerations

### Production Checklist
- [ ] Environment variables secured (not in repository)
- [ ] SSL/TLS certificates configured
- [ ] Database credentials rotated
- [ ] JWT secrets generated (256-bit minimum)
- [ ] Rate limiting enabled
- [ ] CORS configured properly
- [ ] Security headers enabled
- [ ] Database backups automated
- [ ] Monitoring and alerting configured
- [ ] Log rotation configured

### Network Security
- Segregated networks (frontend, backend, cache)
- Non-root user execution
- Resource limits (CPU/memory)
- Regular security updates

## 📖 Additional Resources

- [Main README](../../README.md) - Project overview and development setup
- [CLAUDE.md](../../CLAUDE.md) - AI assistant guidance for this project
- Template-specific READMEs:
  - [template_api](../../template_api/README.md)
  - [template_web](../../template_web/README.md)
  - [template_consola](../../template_consola/README.md)
  - [template_repositorio](../../template_repositorio/README.md)

## 🆘 Troubleshooting

### Common Issues

**Services not starting:**
```bash
make logs        # Check logs
make health      # Verify health status
docker ps -a     # Check container status
```

**Database connection issues:**
- Verify `.env` database credentials
- Ensure PostgreSQL service is running
- Check network connectivity

**SSL certificate errors:**
- Verify certificate paths in nginx.production.conf
- Ensure certificates are not expired
- Check file permissions

For more detailed troubleshooting, consult the specific deployment guide for your chosen method.

## 📝 Version History

- **v2.0.0** (2025-01-24) - Complete English translation and documentation reorganization
- **v1.0.0** (2025-01-10) - Initial production deployment guides

---

**Need Help?** Refer to the specific guide for your deployment method, or check the main project README for development setup.
