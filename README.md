# GitHub Actions Cloudflare Tunnel Runner

This project sets up a temporary server infrastructure using GitHub Actions as a runner, with a Cloudflare Tunnel to expose services running on the GitHub Actions runner to the internet.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         GitHub Actions Runner                                │
│  (Ubuntu - Temporary VM)                                                     │
│                                                                              │
│  ┌──────────────────┐         ┌──────────────────┐                         │
│  │  HTTP Server     │         │   cloudflared     │                         │
│  │  localhost:8000  │◄────────│   tunnel client   │                         │
│  └──────────────────┘         └────────┬─────────┘                         │
│                                         │                                    │
└─────────────────────────────────────────│────────────────────────────────────┘
                                          │
                                          ▼
                              ┌───────────────────────┐      ┌─────────────┐
                              │   Cloudflare Edge     │─────►│  Internet   │
                              │   (Tunnel Gateway)    │      │  (You)      │
                              └───────────────────────┘      └─────────────┘
```

**Key Point**: The Cloudflare Tunnel is created **on the GitHub Actions Runner**, not on your local PC. Your PC only needs to access the public Cloudflare URL.

## Prerequisites

1. A GitHub repository
2. A Cloudflare account (free tier works)
3. Cloudflare Tunnel token from Cloudflare

## Setup Instructions

### Step 1: Create a Cloudflare Tunnel

1. Log in to [Cloudflare Zero Trust](https://one.dash.cloudflare.com/)
2. Go to **Networks** → **Tunnels**
3. Click **Create a tunnel**
4. Choose **Cloudflared** as the connector
5. Give the tunnel a name (e.g., `github-actions-runner`)
6. Save the tunnel token (you'll need this for GitHub Secret)

### Step 2: Add GitHub Secrets

Go to your GitHub repository → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**:

| Secret Name | Value |
|-------------|-------|
| `CLOUDFLARE_TUNNEL_TOKEN` | The tunnel token from Step 1 |

### Step 3: Run the Workflow

1. Go to your repository's **Actions** tab
2. Select **Cloudflare Tunnel Runner** workflow
3. Click **Run workflow**
4. Wait for the workflow to start
5. Check the workflow log for the Cloudflare tunnel URL

### Step 4: Access Your Service

The tunnel URL will be printed in the workflow log. Look for a line like:
```
Your quick Tunnel has been created! Visit https://xxxxx-xxxxx-xxxxx-xxxxx.trycloudflare.com
```

Visit that URL from your browser to access your service.

## Files Structure

```
├── .github/
│   └── workflows/
│       └── cloudflare-tunnel.yml    # Main workflow file
├── services/
│   └── http-server.py              # Example HTTP server
└── README.md
```

## How It Works

1. **Workflow Trigger**: The workflow runs on `workflow_dispatch`, so you can manually start it from GitHub.

2. **Runner Setup**: GitHub allocates a temporary Ubuntu VM.

3. **Service Start**: The HTTP server starts on `localhost:8000` in the background.

4. **Tunnel Creation**: `cloudflared` connects to Cloudflare using your tunnel token and creates a public URL.

5. **Traffic Flow**:
   ```
   You → Cloudflare URL → Cloudflare Edge → Tunnel → GitHub Runner:8000
   ```

6. **Cleanup**: When you cancel the workflow or it times out (60 minutes), everything is terminated.

## Extending for Other Services

### Python Application

Replace the HTTP server step with your Python app:

```yaml
- name: Start Python service
  run: |
    pip install -r requirements.txt
    python your_app.py &
    echo $! > /tmp/service.pid
```

### Node.js Application

```yaml
- name: Start Node.js service
  run: |
    npm install
    node server.js &
    echo $! > /tmp/service.pid
```

### PHP Application

```yaml
- name: Start PHP service
  run: |
    php -S localhost:8000 -t /path/to/public &
    echo $! > /tmp/service.pid
```

### FFmpeg Stream

```yaml
- name: Start FFmpeg stream
  run: |
    ffmpeg -i input -f mpegts http://localhost:8000/stream &
    echo $! > /tmp/service.pid
```

## Configuration

### Changing the Port

Modify the port in two places:
1. The service startup command (e.g., `python3 -m http.server 9000`)
2. The cloudflared tunnel URL (Cloudflare automatically proxies traffic)

### Extending Timeout

The default timeout is 60 minutes. To change:
```yaml
jobs:
  runner:
    runs-on: ubuntu-latest
    timeout-minutes: 120  # Increase as needed
```

## Important Notes

- **Temporary**: Everything is deleted when the workflow ends
- **No Persistence**: Don't expect files to persist between runs
- **Resource Limits**: GitHub Actions has CPU/memory limits
- **Network**: Outbound connections from the runner are limited

## Troubleshooting

### Tunnel doesn't start
- Verify `CLOUDFLARE_TUNNEL_TOKEN` secret is correct
- Check if the tunnel is still valid in Cloudflare dashboard

### Service not accessible
- Ensure your service is binding to `localhost`, not `127.0.0.1`
- Check the service is running: `curl http://localhost:8000`

### Workflow times out
- The default timeout is 60 minutes
- Cancel and rerun if needed

## Security Considerations

- Never hardcode Cloudflare tokens in workflow files
- Use GitHub Secrets for all sensitive data
- The tunnel URL is public - don't share it unless intended
- Consider using authentication on your service