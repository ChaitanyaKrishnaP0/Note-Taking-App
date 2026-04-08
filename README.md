# Python App Deployment as a System Service

This project demonstrates how to deploy a Python application as a **systemd service** on Linux.  
The app will automatically start on system boot and restart if it crashes.

---

## 1. Directory Setup

1. Create a folder for your app:

```bash
mkdir -p ~/deployed_app
cd ~/deployed_app
