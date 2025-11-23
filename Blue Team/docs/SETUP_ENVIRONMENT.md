# Setting Up the Development Environment

## Quick Start

After migrating to environment-based secret management, you must create a `.env` file before running the application.

### Step 1: Copy the Template

```bash
cp .env.example .env
```

### Step 2: Generate Secure Secrets

Generate cryptographically secure random values for each secret:

```bash
# Generate all three secrets at once
python3 -c "import secrets; print('AGENT_SIG_SECRET=' + secrets.token_urlsafe(32)); print('MCP_SIG_SECRET=' + secrets.token_urlsafe(32)); print('ADMIN_SECRET_KEY=' + secrets.token_urlsafe(32))"
```

**Example output:**
```
AGENT_SIG_SECRET=CBD5Pnok-IA7UNQC27Wf_P6ftOLZpRaPXmK7dDLJYNg
MCP_SIG_SECRET=ovyWoP_CZv8iwRbpy7hsqTz2_u1XTuMEGdw-s5YzFSo
ADMIN_SECRET_KEY=kudv3uhjY_6TDgNO1LwyUdfDLiT48SVaZP2lQQAZ66o
```

### Step 3: Update .env File

Open `.env` in your editor and replace the placeholder values with the generated secrets:

```bash
# .env file
AGENT_SIG_SECRET=<your-generated-value-here>
MCP_SIG_SECRET=<your-generated-value-here>
ADMIN_SECRET_KEY=<your-generated-value-here>

# Optional: MCP Server URL (defaults to http://localhost:8001)
MCP_URL=http://localhost:8001

APP_ENV=development
DEBUG_MODE=true
LOG_LEVEL=INFO
```

### Step 4: Secure the File

Set restrictive file permissions (Unix/Linux/Mac):

```bash
chmod 600 .env
```

### Step 5: Verify Setup

Test that the application can load environment variables:

```bash
python3 -c "from dotenv import load_dotenv; import os; load_dotenv(); print('✅ AGENT_SIG_SECRET loaded' if os.getenv('AGENT_SIG_SECRET') else '❌ Missing AGENT_SIG_SECRET')"
```

## Running the Application

### Install Dependencies

If you haven't already installed python-dotenv:

```bash
pip install python-dotenv
```

### Start Main Server

```bash
# Load environment variables and start main server
uvicorn app.main:app --reload --port 8000
```

### Start MCP Server (Separate Terminal)

```bash
# Load environment variables and start MCP server
uvicorn app.mcp_server:app --reload --port 8001
```

## For E2E Testing

When running the E2E test suite, the test script will automatically load environment variables from `.env`:

```bash
python run_e2e_comprehensive.py --base-url http://localhost:8000
```

## Security Best Practices

### ✅ DO
- Use different secrets for each environment (dev/staging/production)
- Rotate secrets quarterly or when compromised
- Restrict file permissions (600 or 400)
- Keep `.env` locally only - never commit to git

### ❌ DON'T
- Commit `.env` files to version control (already in `.gitignore`)
- Share secrets via email, chat, or unencrypted channels
- Use the same secrets across multiple environments
- Hardcode secrets in source code

## Troubleshooting

### Error: "AGENT_SIG_SECRET environment variable must be set"

**Cause**: Application cannot find the `.env` file or it's empty.

**Solution**:
1. Verify `.env` exists in project root
2. Check that all required secrets are set
3. Ensure you're running from the project root directory

### Error: "ModuleNotFoundError: No module named 'dotenv'"

**Cause**: python-dotenv package not installed.

**Solution**:
```bash
pip install python-dotenv
```

### Testing Without .env File

For quick testing, you can set environment variables directly:

```bash
export AGENT_SIG_SECRET="test-secret-1"
export MCP_SIG_SECRET="test-secret-2"
export ADMIN_SECRET_KEY="test-secret-3"

uvicorn app.main:app --reload --port 8000
```

**Note**: These will only persist for the current terminal session.

## Production Deployment

For production environments:

1. **DO NOT** use the values from `.env.example`
2. **ROTATE** all secrets to new cryptographically secure values
3. **USE** a proper secret management service (HashiCorp Vault, AWS Secrets Manager, etc.)
4. **ENABLE** automatic secret rotation
5. **AUDIT** secret access regularly

See `docs/PRINCIPLE_OF_LEAST_PRIVILEGE.md` for detailed production security guidelines.
