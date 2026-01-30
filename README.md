# Server Pinger - Docker Monitoring Project

A simple server availability monitoring system built with Docker.

## Features

- **Real-time Monitoring**: Ping servers at regular intervals
- **Web Interface**: Clean UI with auto-refresh
- **Reverse Proxy**: Nginx for production-grade request handling
- **Health Checks**: Built-in container health monitoring
- **Multi-stage Build**: Optimized Docker images for smaller size
- **Security**: Non-root user execution
- **Configuration**: Environment variables and volume mounts
- **Orchestration**: Docker Compose for multi-container management

## Quick Start

```bash
# Build and start the stack
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the stack
docker-compose down
```

Access the web interface at: `http://localhost:8080`

## Configuration

### Hosts to Monitor

Edit `config/hosts.txt` to add servers you want to monitor:

```
# Add one host per line
google.com
8.8.8.8
github.com
your-server.com
```

Lines starting with `#` are treated as comments and ignored.

### Environment Variables

Configure the application by editing `.env`:

| Variable | Description | Default |
|----------|-------------|---------|
| `CHECK_INTERVAL` | How often to ping servers (seconds) | `30` |
| `NGINX_PORT` | Port to expose on host machine | `8080` |

Example:
```bash
CHECK_INTERVAL=60
NGINX_PORT=9000
```

## Project Structure

```
.
├── app.py              # Flask application
├── Dockerfile          # Multi-stage Docker build
├── docker-compose.yml  # Container orchestration
├── nginx.conf          # Reverse proxy configuration
├── requirements.txt    # Python dependencies
├── .env               # Environment configuration
├── .gitignore         # Git ignore rules
└── config/
    └── hosts.txt      # List of hosts to monitor
```

## Architecture

```
┌─────────────┐
│   Browser   │
└──────┬──────┘
       │ :8080
       ▼
┌─────────────┐
│    Nginx    │ (Reverse Proxy)
└──────┬──────┘
       │ :80
       ▼
┌─────────────┐
│   Pinger    │ (Flask App)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Servers   │ (ICMP Ping)
└─────────────┘
```

## Docker Best Practices Demonstrated

### ✅ Multi-stage Build
Reduces final image size by separating build and runtime dependencies:
- **Builder stage**: Installs Python packages
- **Runtime stage**: Contains only necessary files

### ✅ Health Checks
Both containers include health checks for monitoring:
```bash
# Check container health
docker-compose ps
```

### ✅ Non-root User
Application runs as `appuser` (UID 1000) for security:
```dockerfile
USER appuser
```

### ✅ Custom Network
Containers communicate on isolated bridge network:
```yaml
networks:
  pinger-network:
    driver: bridge
```

### ✅ Volume Mounts
Configuration stored outside containers for persistence:
```yaml
volumes:
  - ./config:/app/config:ro
```

### ✅ Environment Variables
Externalized configuration for different environments:
```yaml
environment:
  - CHECK_INTERVAL=${CHECK_INTERVAL:-30}
```

### ✅ Restart Policies
Automatic container restart on failure:
```yaml
restart: unless-stopped
```

## Monitoring & Debugging

### View Logs

```bash
# All containers
docker-compose logs -f

# Specific container
docker-compose logs -f pinger
docker-compose logs -f nginx
```

### Check Container Status

```bash
# List containers with health status
docker-compose ps

# Detailed container information
docker inspect server-pinger

# Resource usage
docker stats
```

### Test Health Endpoints

```bash
# Pinger health check
curl http://localhost:8080/health

# Direct pinger access (bypassing nginx)
docker exec server-pinger curl http://localhost:5000/health
```

### Debug Container

```bash
# Execute shell in container
docker exec -it server-pinger sh

# Check if ping works
docker exec server-pinger ping -c 1 google.com

# View Python packages
docker exec server-pinger pip list
```

## Backup & Restore

### Backup Configuration

```bash
# Backup hosts configuration
docker run --rm \
  -v pinger_config:/data \
  -v $(pwd):/backup \
  alpine tar czf /backup/config-backup.tar.gz -C /data .
```

### Restore Configuration

```bash
# Restore from backup
docker run --rm \
  -v pinger_config:/data \
  -v $(pwd):/backup \
  alpine tar xzf /backup/config-backup.tar.gz -C /data
```

## Troubleshooting

### Containers Won't Start

```bash
# Check logs for errors
docker-compose logs

# Verify all files are present
ls -la

# Rebuild from scratch
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Can't Access Web Interface

```bash
# Check if port is available
netstat -tlnp | grep 8080

# Verify nginx is running
docker-compose ps nginx

# Check nginx logs
docker-compose logs nginx
```

### All Servers Show DOWN

```bash
# Test ping from container
docker exec server-pinger ping -c 1 google.com

# Check hosts.txt format
docker exec server-pinger cat /app/config/hosts.txt

# Verify permissions
docker exec server-pinger ls -la /app/config/
```

### Application Crashes on Startup

```bash
# Check Python dependencies
docker exec server-pinger python -c "import flask; print(flask.__version__)"

# View full error trace
docker-compose logs pinger

# Rebuild image
docker-compose build --no-cache pinger
```

## Security Notes

- Application runs as non-root user
- Read-only volume mounts where possible
- No sensitive data in environment variables
- Health checks don't expose sensitive information
- Regular base image updates recommended

## License

This project is provided as-is for educational and demonstration purposes.

## Contributing

This is a demonstration project. Feel free to fork and modify for your needs.