# Security Critical Files Registry

**Document Purpose**: Registry of security-critical files requiring mandatory human review before merge/deployment  
**Last Updated**: 2025-11-20  
**Owner**: Security Team  

---

## Overview

This document identifies all files in the Blue Team AI Governance project that contain security-critical code. Changes to these files MUST be reviewed by a security team member before being merged or deployed.

**Review Policy**: All changes to files marked as CRITICAL must be approved by at least one security team member familiar with the MAESTRO framework and AI security best practices.

---

## Security-Critical Files

### 🔴 CRITICAL - Authentication & Secret Management

#### `app/main.py`
**Category**: Authentication, Secret Management, API Security  
**Lines of Interest**:
- Lines 1-10: Environment variable loading (dotenv)
- Lines 1728-1757: Secret management (AGENT_SIG_SECRET, MCP_SIG_SECRET, ADMIN_SECRET_KEY)
- Lines 1759-1771: Admin authentication logic
- Lines 1783-1797: Agent signature verification
- Lines 1850+: Authentication endpoints (/auth/login, /auth/signup)

**Review Requirements**:
- ✅ All secret handling changes
- ✅ Authentication logic modifications
- ✅ Admin authorization changes
- ✅ API endpoint security updates

**Security Comments Added**: ⚠️ Lines 1728-1731 (SECURITY-CRITICAL marker)

---

#### `app/mcp_server.py`
**Category**: Agent Communication Security, Signature Validation  
**Lines of Interest**:
- Lines 1-20: Imports and environment loading
- Lines 30-42: AGENT_SIG_SECRET configuration
- Lines 56-86: Agent signature verification logic
- Lines 77-86: 403 Forbidden response on invalid signature

**Review Requirements**:
- ✅ Signature verification algorithm changes
- ✅ Agent authentication updates
- ✅ MCP protocol security modifications

**Security Comments Added**: ⚠️ Lines 30-35 (SECURITY-CRITICAL marker)

---

#### `app/agent.py`
**Category**: Agent Security, Orchestration Logic  
**Lines of Interest**:
- Lines 1-27: Imports and secret configuration
- Lines 14-27: AGENT_SIG_SECRET and MCP_URL setup
- Lines 54: Deny list configuration (DENY_LIST)
- Lines 143-234: MCP message sending with signature
- Lines 291-330: Deny list security checks
- Lines 389-426: Identity validation logic

**Review Requirements**:
- ✅ Deny list modifications
- ✅ Security boundary changes
- ✅ Identity validation updates
- ✅ Agent signature handling

**Security Comments Added**: ⚠️ Lines 14-20 (SECURITY-CRITICAL marker)

---

### 🟡 HIGH - Configuration & Infrastructure

#### `.env.example`
**Category**: Secret Management Template  
**Purpose**: Template for environment variable configuration

**Review Requirements**:
- ✅ New secret additions
- ✅ Secret naming changes
- ✅ Default value modifications

**Warning**: This file is safe to commit (contains placeholders only). The actual `.env` file is in `.gitignore`.

---

#### `.github/workflows/security-scan.yml`
**Category**: CI/CD Security Pipeline  
**Purpose**: Automated security scanning workflow

**Review Requirements**:
- ✅ Scan policy changes (e.g., severity thresholds)
- ✅ Tool version updates
- ✅ Workflow trigger modifications

---

#### `.pre-commit-config.yaml`
**Category**: Pre-commit Security Hooks  
**Purpose**: Local development security checks

**Review Requirements**:
- ✅ Hook additions/removals
- ✅ Security tool configuration changes
- ✅ Exclusion pattern updates

---

#### `requirements.txt`
**Category**: Dependency Management  
**Lines of Interest**:
- Lines 10-12: Security libraries (passlib, cryptography, pyjwt)
- Lines 14: python-dotenv
- Lines 21-24: Security scanning tools

**Review Requirements**:
- ✅ Security library version updates
- ✅ New cryptography dependencies
- ✅ Removal of security tools

---

### 🟢 MEDIUM - Business Logic & Data Handling

#### `app/expense_agent.py`
**Category**: Business Logic, Financial Processing  
**Lines of Interest**:
- Policy enforcement logic
- Amount validation
- Employee verification

**Review Requirements**:
- ⚠️ Policy limit changes
- ⚠️ Validation logic modifications

---

#### `app/tools.py`
**Category**: Mock Data, HR System Integration  
**Lines of Interest**:
- Lines 52-68: Employee mock data (contains PII)

**Review Requirements**:
- ⚠️ Data structure changes
- ⚠️ Mock data updates

**Note**: Contains demo PII - acceptable for development, must be replaced in production

---

#### `run_e2e_comprehensive.py`
**Category**: Security Testing  
**Lines of Interest**:
- Lines 30-37: Admin token loading from environment

**Review Requirements**:
- ⚠️ Test case modifications affecting security
- ⚠️ Admin token handling changes

---

## Review Workflow

### Pre-Merge Checklist

For all changes to CRITICAL files:

1. **Code Review**
   - [ ] Security team member assigned as reviewer
   - [ ] Changes explained with security rationale
   - [ ] No hardcoded secrets introduced
   - [ ] Authentication/authorization logic validated

2. **Testing Requirements**
   - [ ] Unit tests pass for security functions
   - [ ] E2E security tests pass (run_e2e_comprehensive.py)
   - [ ] Manual security verification completed

3. **Scanning Requirements**
   - [ ] Bandit SAST scan passes (no high-severity issues)
   - [ ] Safety SCA scan passes (no known vulnerabilities)
   - [ ] detect-secrets scan passes (no secrets detected)

4. **Documentation**
   - [ ] Security impact documented in PR description
   - [ ] SECURITY_CRITICAL_FILES.md updated if needed
   - [ ] Deployment instructions updated if configuration changed

---

## Security Review Process

### Step 1: Automated Checks

```bash
# Run all security scans locally before submitting PR
pre-commit run --all-files
bandit -r app/ -ll
safety check
detect-secrets scan --all-files
```

### Step 2: Manual Review

Security reviewer must verify:
- Secret management practices followed
- No credentials exposed
- Authentication logic sound
- Authorization checks present
- Input validation implemented
- Error handling doesn't leak sensitive info

### Step 3: Approval

Required approvals:
- **CRITICAL files**: 1 security team member + 1 senior engineer
- **HIGH files**: 1 security team member
- **MEDIUM files**: 1 team member (security review recommended)

---

## Emergency Hotfix Procedure

For urgent security fixes:

1. **Immediate Response**
   - Create hotfix branch from main
   - Implement minimal fix
   - Run security scans

2. **Expedited Review**
   - Tag security team lead for immediate review
   - Conduct pair programming session if possible
   - Document security incident

3. **Post-Deployment**
   - Conduct security retrospective within 24 hours
   - Update security documentation
   - Schedule follow-up improvements

---

## File Change Log

Track significant security-related changes:

| Date | File | Change | Reviewer | Ticket |
|------|------|--------|----------|--------|
| 2025-11-20 | `app/main.py` | Migrated secrets to env vars | Security Team | SEC-001 |
| 2025-11-20 | `app/mcp_server.py` | Migrated secrets to env vars | Security Team | SEC-001 |
| 2025-11-20 | `app/agent.py` | Migrated secrets to env vars | Security Team | SEC-001 |
| 2025-11-20 | `.pre-commit-config.yaml` | Added security hooks | Security Team | SEC-002 |

---

## Security Incident Response

If a security issue is discovered in a critical file:

1. **Immediately notify**: security-team@company.com
2. **Assess impact**: Determine scope of exposure
3. **Rotate secrets**: If credentials compromised
4. **Deploy fix**: Follow hotfix procedure
5. **Document**: Update incident log
6. **Review**: Conduct post-mortem

---

## Appendix: Security Markers in Code

All security-critical sections are marked with:

```python
# ⚠️ SECURITY-CRITICAL: [Component Name]
# MANDATORY HUMAN REVIEW REQUIRED before merge
# [Description of what requires review]
```

Use `grep -r "SECURITY-CRITICAL" app/` to find all marked sections.

---

## Contact & Escalation

**Security Team Lead**: security-lead@company.com  
**On-call Security**: security-oncall@company.com  
**Escalation Point**: ciso@company.com  

**For non-urgent questions**: #security-reviews (Slack)  
**For urgent issues**: Page security-oncall immediately
