# 🐳 Docker Compose Guide - HabitFlow

Complete `docker-compose.yml` configuration with everything automated!

## 🚀 Quick Start (One Command)

```bash
cd /c/Users/arung/OneDrive/Desktop/Hackathon/habit-tracker
docker-compose up
```

**That's it! The app will start automatically.** ✨

---

## 📋 Complete Commands

### **1. Start (Build & Run)**
```bash
docker-compose up
```

### **2. Start in Background (Daemon Mode)**
```bash
docker-compose up -d
```

### **3. View Live Logs**
```bash
docker-compose logs -f habitflow
```

### **4. View Container Status**
```bash
docker-compose ps
```

### **5. Stop Container**
```bash
docker-compose down
```

### **6. Stop & Remove All (Clean)**
```bash
docker-compose down -v
```

### **7. Rebuild Image**
```bash
docker-compose build --no-cache
```

### **8. Restart Container**
```bash
docker-compose restart
```

### **9. Execute Command in Container**
```bash
docker-compose exec habitflow python
```

### **10. View Container Stats**
```bash
docker stats
```

---

## 🌐 Access the Application

Once running:

```
http://localhost:5000
```

---

## 📊 What's Configured

### **Services**
- ✅ HabitFlow Flask App (Python 3.11)

### **Ports**
- ✅ 5000:5000 (Flask app)

### **Volumes**
- ✅ `habitflow-data` - Database storage (persistent)
- ✅ `habitflow-logs` - Application logs

### **Networks**
- ✅ `habitflow-network` - Internal bridge network

### **Environment Variables**
- ✅ FLASK_APP: app.py
- ✅ FLASK_ENV: production
- ✅ DATABASE_URL: sqlite:///instance/habit_tracker.db
- ✅ SECRET_KEY: configured
- ✅ JWT_SECRET_KEY: configured

### **Health Checks**
- ✅ Monitors app every 30 seconds
- ✅ Auto-restarts if unhealthy
- ✅ 40-second grace period on startup

### **Restart Policy**
- ✅ Auto-restarts unless stopped manually

---

## 🔍 Example Workflow

```bash
# 1. Navigate to project
cd /c/Users/arung/OneDrive/Desktop/Hackathon/habit-tracker

# 2. Start everything with one command
docker-compose up -d

# 3. Check logs
docker-compose logs -f

# 4. Open browser
# Visit: http://localhost:5000

# 5. Register account and use the app

# 6. When done, stop it
docker-compose down
```

---

## 🛠️ Customize Configuration

Edit `docker-compose.yml` to change:

### **Change Port**
```yaml
ports:
  - "8080:5000"  # Change 8080 to your port
```

### **Change Environment Variables**
```yaml
environment:
  SECRET_KEY: your-secret-key
  JWT_SECRET_KEY: your-jwt-secret
  DEBUG: 1  # Enable debug mode
```

### **Add Database Service (MySQL/PostgreSQL)**
```yaml
database:
  image: mysql:latest
  environment:
    MYSQL_ROOT_PASSWORD: root
    MYSQL_DATABASE: habit_tracker
  volumes:
    - db-data:/var/lib/mysql
  networks:
    - habitflow-network

volumes:
  db-data:
```

---

## 📁 Project Structure

```
habit-tracker/
├── Dockerfile              # Container build instructions
├── docker-compose.yml      # Orchestration & configuration
├── .dockerignore          # Files to exclude from build
├── app.py                 # Flask app
├── models.py              # Database models
├── config.py              # Configuration
├── requirements.txt       # Python dependencies
├── routes/                # API routes
├── services/              # Business logic
├── templates/             # HTML pages
├── static/               # CSS/JS
└── instance/             # SQLite database (persistent)
```

---

## 🎯 Features

✅ **One-Command Setup** - `docker-compose up`
✅ **Persistent Data** - Database survives restarts
✅ **Health Monitoring** - Auto-restarts if unhealthy
✅ **Log Streaming** - Easy debugging
✅ **Environment Management** - All config centralized
✅ **Network Isolation** - Safe networking
✅ **Volume Management** - Data persistence
✅ **Production Ready** - Best practices applied

---

## 🐛 Troubleshooting

### **Port Already in Use**
```bash
# Option 1: Change port in docker-compose.yml
# ports:
#   - "8080:5000"

# Option 2: Kill process using port
lsof -i :5000
kill -9 <PID>
```

### **Container Won't Start**
```bash
# Check logs
docker-compose logs habitflow

# Rebuild from scratch
docker-compose build --no-cache
docker-compose up
```

### **Database Issues**
```bash
# Remove volumes and restart
docker-compose down -v
docker-compose up
```

### **Permission Denied**
```bash
# On Linux/Mac: Add Docker to user group
sudo usermod -aG docker $USER
newgrp docker
```

---

## 📊 Container Info

- **Name**: habitflow-app
- **Image**: habitflow:latest
- **Network**: habitflow-network
- **Restart**: unless-stopped
- **TTY**: Enabled (interactive)

---

## 🔄 Upgrading

### **Pull Latest Code & Rebuild**
```bash
docker-compose down
git pull origin main
docker-compose build --no-cache
docker-compose up -d
```

---

## 📈 Monitoring

### **View Real-time Stats**
```bash
docker stats
```

### **View Container Details**
```bash
docker inspect habitflow-app
```

### **View Network Info**
```bash
docker network inspect habitflow-network
```

---

## 🔐 Security Tips

1. **Change default secrets in docker-compose.yml**
2. **Use environment files (.env) for sensitive data**
3. **Don't commit `.env` to Git**
4. **Use HTTPS in production**
5. **Keep images updated**

---

## 🚀 Production Deployment

### **Using Environment File**

Create `.env`:
```env
FLASK_ENV=production
SECRET_KEY=your-production-secret
JWT_SECRET_KEY=your-production-jwt-key
DATABASE_URL=postgresql://user:pass@db:5432/habitflow
DEBUG=0
```

Update `docker-compose.yml`:
```yaml
env_file:
  - .env
```

---

## 📚 Learning Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Docs](https://docs.docker.com/compose/)
- [Flask Docker Guide](https://flask.palletsprojects.com/deployment/docker/)

---

## ✨ That's It!

Run one command and HabitFlow is up and running:

```bash
docker-compose up -d
```

Then visit: **http://localhost:5000**

🎉 **Enjoy your containerized habit tracker!**
