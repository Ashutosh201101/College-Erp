# 🎓 College ERP System — IILM University

Cloud-Native Flask ERP | Docker + GitHub Actions + AWS EC2 Auto Scaling

**Author:** Ashutosh Chakrawal | Roll: 25SCS2040002238 | IILM University, Greater Noida

---

## 📁 Project Structure

```
college-erp/
├── app.py                          # Main Flask application
├── requirements.txt                # Python dependencies
├── Dockerfile                      # Container build file
├── docker-compose.yml              # Local development setup
├── .github/
│   └── workflows/
│       └── deploy.yml              # CI/CD pipeline (GitHub Actions)
└── templates/
    ├── base.html                   # Base layout with nav + sidebar
    ├── login.html                  # Login page
    ├── admin_dashboard.html        # Admin home
    ├── admin_students.html         # Student management
    ├── admin_courses.html          # Course management
    ├── admin_fees.html             # Fee management
    ├── student_dashboard.html      # Student home
    └── grades.html                 # Grade report
```

---

## 🚀 Day 1 — Local Setup & Test

### Step 1: Run Locally with Docker

```bash
# Make sure Docker Desktop is installed and running
docker-compose up --build

# Open browser: http://localhost:5000
# Admin login:   admin@iilm.edu / admin123
# Student login: ashutosh@iilm.edu / student123
```

### Step 2: Test Health Check

```bash
curl http://localhost:5000/health
# Expected: {"status": "healthy", "version": "1.0.0"}
```

---

## ☁️ Day 2 — AWS Deployment

### Step 1: Push Code to GitHub

```bash
git init
git add .
git commit -m "initial commit: College ERP"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/college-erp.git
git push -u origin main
```

### Step 2: Create AWS ECR Repository

1. Go to AWS Console → ECR → Create Repository
2. Name: `college-erp`
3. Private, default settings

### Step 3: Launch EC2 Instance

1. AWS Console → EC2 → Launch Instance
2. AMI: **Amazon Linux 2**
3. Type: **t2.micro** (Free Tier)
4. Security Group: Allow **Port 80** (HTTP) and **Port 22** (SSH)
5. Create/download `.pem` key pair
6. Install Docker on EC2:

```bash
sudo yum update -y
sudo yum install docker -y
sudo service docker start
sudo usermod -a -G docker ec2-user
sudo reboot
```

### Step 4: Add GitHub Secrets

Go to your GitHub repo → Settings → Secrets and Variables → Actions → New Secret:

| Secret Name            | Value                              |
|------------------------|------------------------------------|
| `AWS_ACCESS_KEY_ID`    | Your AWS IAM access key ID         |
| `AWS_SECRET_ACCESS_KEY`| Your AWS IAM secret key            |
| `EC2_HOST`             | EC2 public IP address              |
| `EC2_SSH_KEY`          | Content of your .pem file          |
| `SECRET_KEY`           | Any random string e.g. `erp2025`  |

### Step 5: Deploy!

```bash
git push origin main
# GitHub Actions will automatically:
# 1. Build Docker image
# 2. Push to AWS ECR
# 3. SSH into EC2
# 4. Deploy new container
# Total time: ~2 min 43 sec
```

---

## 📈 Day 3 — Auto Scaling Setup

### Create Auto Scaling Group

1. AWS Console → EC2 → Auto Scaling Groups → Create
2. **Min:** 1, **Desired:** 1, **Max:** 3
3. Scaling Policy: Target Tracking → CPUUtilization
4. **Scale Out:** CPU > 60%
5. **Scale In:** CPU < 30%
6. Attach Application Load Balancer (ALB)

### Load Test (Show it scaling live!)

```bash
# Install Apache Bench
sudo apt-get install apache2-utils -y  # Ubuntu
# OR
brew install httpd  # Mac

# Run load test (keep AWS Console open to watch!)
ab -n 2000 -c 100 http://YOUR-ALB-URL/

# Watch in AWS Console:
# EC2 → Auto Scaling Groups → Activity
# Instances will scale: 1 → 2 → 3 automatically
```

---

## 🔑 Default Login Credentials

| Role    | Email                    | Password      |
|---------|--------------------------|---------------|
| Admin   | admin@iilm.edu           | admin123      |
| Student | ashutosh@iilm.edu        | student123    |
| Student | rishabh@iilm.edu         | student123    |
| Student | priya@iilm.edu           | student123    |

---

## 🛠 Tech Stack

- **Backend:** Python Flask 3.0 + SQLite
- **Frontend:** HTML5, CSS3, Jinja2 Templates
- **Container:** Docker (python:3.11-slim) ~185 MB
- **CI/CD:** GitHub Actions
- **Cloud:** AWS EC2 (t2.micro) + ECR + ALB + Auto Scaling + CloudWatch
- **Region:** ap-south-1 (Mumbai)

---

## 📊 Performance Results

| Metric                | Result              |
|-----------------------|---------------------|
| Pipeline Duration     | ~2 min 43 sec       |
| Docker Image Size     | ~185 MB (79% saved) |
| Load Test Errors      | 0 HTTP 5xx          |
| Auto-Scale Trigger    | CPU > 60%           |
| Instances Scaled      | 1 → 3               |

---

*IILM University, Greater Noida | MCA 2025*
# test
