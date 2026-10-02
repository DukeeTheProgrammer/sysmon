# RAT Public Access Guide

## Current Status

**Your Public IP:** `105.116.9.2`

**Dashboard URL:** `http://105.116.9.2:5000`

**Login:** admin / rat_admin_2024

---

## Option 1: Port Forwarding (Recommended for Home Network)

### Steps:
1. Log into your router (usually 192.168.1.1 or 192.168.0.1)
2. Find "Port Forwarding" or "Virtual Server" settings
3. Add a new rule:
   - **External Port:** 5000
   - **Internal IP:** Your machine's local IP (e.g., 192.168.1.100)
   - **Internal Port:** 5000
   - **Protocol:** TCP
4. Save and apply

### Access URL:
```
http://105.116.9.2:5000
```

---

## Option 2: Ngrok (Free, No Port Forwarding Needed)

### Setup:
1. Sign up at https://dashboard.ngrok.com/signup (free)
2. Get your authtoken from the dashboard
3. Run:
```bash
ngrok config add-authtoken YOUR_AUTHTOKEN
ngrok http 5000
```

### Access URL:
```
https://random-name.ngrok-free.app
```

---

## Option 3: Cloudflare Tunnel (Free, Recommended)

### Setup:
1. Install cloudflared:
```bash
curl -L --output cloudflared.deb https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i cloudflared.deb
```

2. Create a tunnel:
```bash
cloudflared tunnel --url http://localhost:5000
```

### Access URL:
```
https://random-name.trycloudflare.com
```

---

## Option 4: Serveo (No Installation)

### Quick Access:
```bash
# Install serveo client
curl -L http://serveo.net/java-client.jar -o serveo.jar

# Start tunnel
java -jar serveo.jar 5000
```

### Access URL:
```
https://random-name.serveo.net
```

---

## Quick Start Script

Run this to start everything with the current public IP:

```bash
cd /home/dukeetheprogrammer/rat
./start_public.sh
```

This will:
1. Start the RAT agent
2. Start the dashboard
3. Send the public URL to your email

---

## Current Public URL

**URL:** `http://105.116.9.2:5000`

**Note:** This IP may change if you're on a dynamic IP. For a permanent URL, use Option 2, 3, or 4 above.

---

## Email Configuration

The dashboard URL has been sent to:
- `ujiroduke1@gmail.com`

You can add more recipients via the dashboard at:
`http://105.116.9.2:5000`

---

## Troubleshooting

### Can't access the dashboard?

1. **Check if dashboard is running:**
```bash
curl http://127.0.0.1:5000/login
```

2. **Check firewall:**
```bash
sudo firewall-cmd --add-port=5000/tcp --permanent
sudo firewall-cmd --reload
```

3. **Check if port is open:**
```bash
sudo netstat -tlnp | grep 5000
```

### Email not received?

1. Check spam folder
2. Verify SendLib API is working
3. Check dashboard logs: `cat /tmp/opencode/rat_dashboard.log`

---

## Security Tips

1. **Change default password** in `rat_agent/config.py`
2. **Use HTTPS** with ngrok/cloudflared
3. **Enable firewall** and only allow necessary ports
4. **Regular updates** to the RAT application
