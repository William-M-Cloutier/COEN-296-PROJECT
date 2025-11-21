from __future__ import annotations

import sys
import requests
import logging
from pathlib import Path

from fastapi import FastAPI, Header, HTTPException, Request, Depends
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Blue Team AI Governance - Enterprise Copilot",
    description="AI-powered expense management with MAESTRO security controls",
    version="1.0.0"
)


LOGIN_HTML = """
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <title>Blue Team Copilot - Login</title>
    <style>
      * { box-sizing: border-box; }
      body {
        margin: 0;
        font-family: "Inter", system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        background: linear-gradient(135deg, #eef2ff 0%, #fdf2f8 45%, #f1f5f9 100%);
        color: #0f172a;
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 100vh;
        padding: 24px;
      }
      .login-container {
        width: 100%;
        max-width: 480px;
        background: #ffffff;
        border-radius: 16px;
        border: 1px solid rgba(15, 23, 42, 0.05);
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.1);
        overflow: hidden;
      }
      .login-header {
        padding: 32px 32px 24px;
        background: linear-gradient(120deg, rgba(79, 70, 229, 0.08), rgba(14, 165, 233, 0.08));
        text-align: center;
      }
      .login-header h1 {
        margin: 0 0 8px;
        font-size: 24px;
        font-weight: 600;
        color: #0f172a;
      }
      .login-header p {
        margin: 0;
        font-size: 14px;
        color: #475569;
      }
      .login-tabs {
        display: flex;
        border-bottom: 1px solid rgba(15, 23, 42, 0.08);
      }
      .login-tab {
        flex: 1;
        padding: 16px;
        background: transparent;
        border: none;
        font-size: 14px;
        font-weight: 500;
        color: #64748b;
        cursor: pointer;
        transition: all 0.2s;
      }
      .login-tab.active {
        color: #4f46e5;
        border-bottom: 2px solid #4f46e5;
        background: rgba(79, 70, 229, 0.05);
      }
      .login-content {
        padding: 32px;
      }
      .login-form {
        display: flex;
        flex-direction: column;
        gap: 20px;
      }
      .form-group {
        display: flex;
        flex-direction: column;
        gap: 8px;
      }
      .form-group label {
        font-size: 14px;
        font-weight: 500;
        color: #374151;
      }
      .form-group input {
        padding: 12px;
        border-radius: 8px;
        border: 1px solid rgba(79, 70, 229, 0.3);
        font-size: 14px;
        background: #ffffff;
      }
      .form-group input:focus {
        outline: none;
        border-color: #4f46e5;
        box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
      }
      .login-button {
        padding: 14px;
        border: none;
        border-radius: 8px;
        background: linear-gradient(120deg, #4f46e5, #0ea5e9);
        color: #ffffff;
        font-size: 15px;
        font-weight: 500;
        cursor: pointer;
        transition: transform 0.1s;
      }
      .login-button:hover {
        transform: translateY(-1px);
      }
      .login-button:disabled {
        opacity: 0.5;
        cursor: not-allowed;
      }
      .error-message {
        padding: 12px;
        border-radius: 8px;
        background: rgba(239, 68, 68, 0.1);
        color: #b91c1c;
        font-size: 14px;
        display: none;
      }
      .error-message.show {
        display: block;
      }
      .success-message {
        padding: 12px;
        border-radius: 8px;
        background: rgba(16, 185, 129, 0.1);
        color: #0f766e;
        font-size: 14px;
        display: none;
      }
      .success-message.show {
        display: block;
      }
      .credential-hint {
        margin-top: 16px;
        padding: 12px;
        border-radius: 8px;
        background: rgba(59, 130, 246, 0.08);
        font-size: 12px;
        color: #1d4ed8;
      }
      .credential-hint strong {
        display: block;
        margin-bottom: 4px;
      }
    </style>
  </head>
  <body>
    <div class="login-container">
      <div class="login-header">
        <h1>Blue Team Enterprise Copilot</h1>
        <p>Secure expense &amp; policy assistant</p>
      </div>
      <div class="login-tabs">
        <button class="login-tab active" data-tab="employee">Employee</button>
        <button class="login-tab" data-tab="admin">Admin</button>
        <button class="login-tab" data-tab="auditor">Auditor</button>
      </div>
      <div class="login-content">
        <!-- Employee Login -->
        <div id="employee-login" class="login-form">
          <div class="form-group">
            <label>Username</label>
            <input type="text" id="emp-username" placeholder="Enter your username" />
          </div>
          <div class="form-group">
            <label>Employee ID (Password)</label>
            <input type="text" id="emp-password" placeholder="Enter your employee ID" />
          </div>
          <button class="login-button" onclick="loginEmployee()">Login</button>
          <div class="error-message" id="emp-error"></div>
        </div>
        <!-- Employee Signup -->
        <div id="employee-signup" class="login-form" style="display: none;">
          <div class="form-group">
            <label>Username</label>
            <input type="text" id="signup-username" placeholder="Choose a username" />
          </div>
          <div class="form-group">
            <label>Employee ID</label>
            <input type="text" id="signup-employee-id" placeholder="e.g., emp-001" />
          </div>
          <button class="login-button" onclick="signupEmployee()">Sign Up</button>
          <div class="error-message" id="signup-error"></div>
          <div class="success-message" id="signup-success"></div>
          <button class="login-button" style="background: rgba(79, 70, 229, 0.1); color: #4f46e5; margin-top: 8px;" onclick="showEmployeeLogin()">Back to Login</button>
        </div>
        <!-- Admin Login -->
        <div id="admin-login" class="login-form" style="display: none;">
          <div class="form-group">
            <label>Username</label>
            <input type="text" id="admin-username" placeholder="Admin" />
          </div>
          <div class="form-group">
            <label>Password</label>
            <input type="password" id="admin-password" placeholder="12345" />
          </div>
          <button class="login-button" onclick="loginAdmin()">Login</button>
          <div class="error-message" id="admin-error"></div>
          <div class="credential-hint">
            <strong>Default Credentials:</strong>
            Username: Admin<br />
            Password: 12345
          </div>
        </div>
        <!-- Auditor Login -->
        <div id="auditor-login" class="login-form" style="display: none;">
          <div class="form-group">
            <label>Username</label>
            <input type="text" id="auditor-username" placeholder="Audit" />
          </div>
          <div class="form-group">
            <label>Password</label>
            <input type="password" id="auditor-password" placeholder="123abc" />
          </div>
          <button class="login-button" onclick="loginAuditor()">Login</button>
          <div class="error-message" id="auditor-error"></div>
          <div class="credential-hint">
            <strong>Default Credentials:</strong>
            Username: Audit<br />
            Password: 123abc
          </div>
        </div>
      </div>
    </div>
    <script>
      let currentTab = "employee";
      const tabs = document.querySelectorAll(".login-tab");
      tabs.forEach(tab => {
        tab.addEventListener("click", () => {
          const tabName = tab.getAttribute("data-tab");
          switchTab(tabName);
        });
      });
      function switchTab(tab) {
        currentTab = tab;
        tabs.forEach(t => t.classList.remove("active"));
        document.querySelector(`[data-tab="${tab}"]`).classList.add("active");
        document.getElementById("employee-login").style.display = tab === "employee" ? "block" : "none";
        document.getElementById("employee-signup").style.display = "none";
        document.getElementById("admin-login").style.display = tab === "admin" ? "block" : "none";
        document.getElementById("auditor-login").style.display = tab === "auditor" ? "block" : "none";
        clearMessages();
      }
      function showEmployeeSignup() {
        document.getElementById("employee-login").style.display = "none";
        document.getElementById("employee-signup").style.display = "block";
        clearMessages();
      }
      function showEmployeeLogin() {
        document.getElementById("employee-signup").style.display = "none";
        document.getElementById("employee-login").style.display = "block";
        clearMessages();
      }
      function clearMessages() {
        document.querySelectorAll(".error-message, .success-message").forEach(el => {
          el.classList.remove("show");
          el.textContent = "";
        });
      }
      function showError(id, message) {
        const el = document.getElementById(id);
        el.textContent = message;
        el.classList.add("show");
      }
      function showSuccess(id, message) {
        const el = document.getElementById(id);
        el.textContent = message;
        el.classList.add("show");
      }
      async function loginEmployee() {
        const username = document.getElementById("emp-username").value.trim();
        const password = document.getElementById("emp-password").value.trim();
        clearMessages();
        if (!username || !password) {
          showError("emp-error", "Please enter both username and employee ID");
          return;
        }
        try {
          const resp = await fetch("/auth/login", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username, password })
          });
          const data = await resp.json();
          if (resp.ok && data.role === "employee") {
            localStorage.setItem("auth_token", data.token);
            localStorage.setItem("username", data.username);
            localStorage.setItem("role", data.role);
            window.location.href = "/";
          } else {
            showError("emp-error", data.detail || "Invalid credentials");
          }
        } catch (err) {
          showError("emp-error", "Network error: " + err.message);
        }
      }
      async function signupEmployee() {
        const username = document.getElementById("signup-username").value.trim();
        const employeeId = document.getElementById("signup-employee-id").value.trim();
        clearMessages();
        if (!username || !employeeId) {
          showError("signup-error", "Please enter both username and employee ID");
          return;
        }
        try {
          const resp = await fetch("/auth/signup", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username, employee_id: employeeId })
          });
          const data = await resp.json();
          if (resp.ok) {
            showSuccess("signup-success", "Account created! You can now login with your username and employee ID.");
            setTimeout(() => showEmployeeLogin(), 2000);
          } else {
            showError("signup-error", data.detail || "Signup failed");
          }
        } catch (err) {
          showError("signup-error", "Network error: " + err.message);
        }
      }
      async function loginAdmin() {
        const username = document.getElementById("admin-username").value.trim();
        const password = document.getElementById("admin-password").value.trim();
        clearMessages();
        if (!username || !password) {
          showError("admin-error", "Please enter both username and password");
          return;
        }
        try {
          const resp = await fetch("/auth/login", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username, password })
          });
          const data = await resp.json();
          if (resp.ok && data.role === "admin") {
            localStorage.setItem("auth_token", data.token);
            localStorage.setItem("username", data.username);
            localStorage.setItem("role", data.role);
            window.location.href = "/";
          } else {
            showError("admin-error", data.detail || "Invalid credentials");
          }
        } catch (err) {
          showError("admin-error", "Network error: " + err.message);
        }
      }
      async function loginAuditor() {
        const username = document.getElementById("auditor-username").value.trim();
        const password = document.getElementById("auditor-password").value.trim();
        clearMessages();
        if (!username || !password) {
          showError("auditor-error", "Please enter both username and password");
          return;
        }
        try {
          const resp = await fetch("/auth/login", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username, password })
          });
          const data = await resp.json();
          if (resp.ok && data.role === "auditor") {
            localStorage.setItem("auth_token", data.token);
            localStorage.setItem("username", data.username);
            localStorage.setItem("role", data.role);
            window.location.href = "/";
          } else {
            showError("auditor-error", data.detail || "Invalid credentials");
          }
        } catch (err) {
          showError("auditor-error", "Network error: " + err.message);
        }
      }
      // Add signup link to employee login
      document.addEventListener("DOMContentLoaded", () => {
        const empLogin = document.getElementById("employee-login");
        const signupLink = document.createElement("button");
        signupLink.type = "button";
        signupLink.textContent = "Don't have an account? Sign Up";
        signupLink.style.cssText = "background: transparent; border: none; color: #4f46e5; cursor: pointer; font-size: 14px; margin-top: 8px; text-decoration: underline;";
        signupLink.onclick = showEmployeeSignup;
        empLogin.appendChild(signupLink);
      });
    </script>
  </body>
</html>
"""

CHAT_HTML = """
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <title>Blue Team Copilot Chat</title>
    <style>
      * { box-sizing: border-box; }
      body {
        margin: 0;
        font-family: "Inter", system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        background: linear-gradient(135deg, #eef2ff 0%, #fdf2f8 45%, #f1f5f9 100%);
        color: #0f172a;
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 24px;
      }
      .chat-shell {
        position: fixed;
        bottom: 20px;
        right: 20px;
        width: 400px;
        height: 600px;
        background: #ffffff;
        border-radius: 12px;
        border: 1px solid #e5e7eb;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
        display: flex;
        flex-direction: column;
        overflow: hidden;
        transition: all 0.3s ease;
        z-index: 1000;
      }
      .chat-shell.minimized {
        height: 60px;
        width: 60px;
        border-radius: 50%;
        overflow: hidden;
      }
      .chat-toggle-btn {
        position: fixed;
        bottom: 20px;
        right: 20px;
        width: 60px;
        height: 60px;
        border-radius: 50%;
        background: linear-gradient(135deg, #4f46e5, #7c3aed);
        color: white;
        border: none;
        cursor: pointer;
        box-shadow: 0 4px 12px rgba(79, 70, 229, 0.4);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 24px;
        z-index: 1001;
        transition: transform 0.2s;
      }
      .chat-toggle-btn:hover {
        transform: scale(1.1);
      }
      .chat-toggle-btn.hidden {
        display: none;
      }
      .main-content {
        padding: 40px;
        max-width: 1400px;
        margin: 0 auto;
      }
      .chat-header {
        padding: 20px 24px;
        border-bottom: 1px solid rgba(15, 23, 42, 0.08);
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: linear-gradient(120deg, rgba(79, 70, 229, 0.08), rgba(14, 165, 233, 0.08));
      }
      .chat-header-title {
        font-weight: 600;
        font-size: 20px;
        color: #0f172a;
      }
      .chat-header-subtitle {
        font-size: 13px;
        color: #475569;
      }
      .role-select {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 13px;
      }
      .role-select select {
        background: rgba(255, 255, 255, 0.85);
        color: #0f172a;
        border: 1px solid rgba(79, 70, 229, 0.35);
        border-radius: 999px;
        padding: 6px 16px;
        font-size: 13px;
        box-shadow: 0 6px 15px rgba(79, 70, 229, 0.15);
      }
      .chat-log {
        padding: 18px 24px;
        height: 420px;
        overflow-y: auto;
        background: linear-gradient(120deg, rgba(14, 165, 233, 0.05), rgba(236, 72, 153, 0.05));
      }
      .message {
        max-width: 80%;
        margin-bottom: 12px;
        padding: 12px 14px;
        border-radius: 12px;
        font-size: 15px;
        line-height: 1.5;
      }
      .message.user {
        margin-left: auto;
        background: linear-gradient(120deg, #4f46e5, #0ea5e9);
        color: #ffffff;
        box-shadow: none;
      }
      .message.agent {
        margin-right: auto;
        background: #ffffff;
        border: 1px solid rgba(15, 23, 42, 0.08);
        box-shadow: none;
      }
      .message.meta {
        margin: 8px auto;
        font-size: 11px;
        color: #6b7280;
        text-align: center;
      }
      .chat-input {
        border-top: 1px solid rgba(15, 23, 42, 0.06);
        padding: 16px 24px;
        background: #ffffff;
      }
      .chat-input-inner {
        display: flex;
        gap: 8px;
      }
      .chat-input textarea {
        flex: 1;
        resize: none;
        min-height: 48px;
        max-height: 120px;
        padding: 12px;
        border-radius: 10px;
        border: 1px solid rgba(79, 70, 229, 0.3);
        background: #ffffff;
        color: #0f172a;
        font-size: 14px;
        box-shadow: none;
      }
      .chat-input button {
        border: none;
        border-radius: 999px;
        padding: 0 24px;
        font-size: 15px;
        font-weight: 500;
        background: linear-gradient(120deg, #ec4899, #8b5cf6);
        color: #ffffff;
        cursor: pointer;
        box-shadow: none;
      }
      .chat-input button:disabled {
        opacity: 0.5;
        cursor: default;
      }
      .hint {
        margin-top: 8px;
        font-size: 12px;
        color: #475569;
      }
      .agent-tags {
        display: none;
      }
      .quick-actions {
        margin-top: 6px;
        display: flex;
        flex-wrap: wrap;
        gap: 6px;
      }
      .quick-actions button {
        border-radius: 999px;
        border: 1px solid rgba(15, 23, 42, 0.08);
        background: rgba(59, 130, 246, 0.08);
        color: #1d4ed8;
        font-size: 12px;
        font-weight: 500;
        padding: 6px 14px;
        cursor: pointer;
        transition: transform 0.1s ease, box-shadow 0.2s ease;
      }
      .quick-actions button:hover {
        background: rgba(59, 130, 246, 0.14);
        transform: translateY(-1px);
        box-shadow: none;
      }
      .forms-container {
        border-top: 1px solid rgba(15, 23, 42, 0.06);
        padding: 20px 24px 28px;
        background: linear-gradient(120deg, rgba(219, 234, 254, 0.6), rgba(255, 228, 230, 0.6));
      }
      .form-section + .form-section {
        margin-top: 16px;
        border-top: 1px solid #e5e7eb;
        padding-top: 16px;
      }
      .form-section h3 {
        margin: 0 0 8px;
        font-size: 15px;
        color: #0f172a;
      }
      .form-section p {
        margin: 0 0 8px;
        font-size: 12px;
        color: #475569;
      }
      .form-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
        gap: 12px;
      }
      .form-grid label {
        display: flex;
        flex-direction: column;
        font-size: 12px;
        color: #374151;
      }
      .form-grid input,
      .form-grid select,
      .form-grid textarea {
        margin-top: 4px;
        padding: 10px;
        border-radius: 10px;
        border: 1px solid rgba(79, 70, 229, 0.25);
        font-size: 13px;
        background: #ffffff;
        box-shadow: none;
      }
      .form-grid textarea {
        min-height: 60px;
        resize: vertical;
      }
      .form-actions {
        margin-top: 12px;
        display: flex;
        justify-content: flex-end;
      }
      .form-actions button {
        border: none;
        border-radius: 8px;
        background: linear-gradient(120deg, #0ea5e9, #14b8a6);
        color: #ffffff;
        padding: 10px 20px;
        cursor: pointer;
        font-size: 14px;
        box-shadow: none;
      }
      .csv-upload textarea {
        width: 100%;
        min-height: 140px;
        padding: 10px;
        border-radius: 10px;
        border: 1px solid rgba(79, 70, 229, 0.25);
        font-size: 12px;
        font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
        resize: vertical;
        background: #ffffff;
      }
      .csv-upload button {
        margin-top: 8px;
        border: none;
        border-radius: 8px;
        background: linear-gradient(120deg, #ec4899, #f97316);
        color: #ffffff;
        padding: 10px 20px;
        cursor: pointer;
        font-size: 14px;
        box-shadow: none;
      }
      .status-feed {
        margin-top: 20px;
        padding: 16px;
        border-radius: 12px;
        border: 1px solid rgba(15, 23, 42, 0.08);
        background: #ffffff;
      }
      .status-feed h3 {
        margin: 0 0 6px;
        font-size: 14px;
        color: #0f172a;
      }
      .status-feed p {
        margin: 0 0 12px;
        font-size: 12px;
        color: #475569;
      }
      .status-items {
        max-height: 180px;
        overflow-y: auto;
        display: flex;
        flex-direction: column;
        gap: 6px;
      }
      .status-item {
        font-size: 13px;
        padding: 8px 10px;
        border-radius: 8px;
        border: 1px solid rgba(15, 23, 42, 0.06);
        background: #f8fafc;
      }
      .status-item.success {
        border-color: rgba(16, 185, 129, 0.4);
        background: rgba(16, 185, 129, 0.08);
        color: #0f766e;
      }
      .status-item.error {
        border-color: rgba(239, 68, 68, 0.4);
        background: rgba(239, 68, 68, 0.08);
        color: #b91c1c;
      }
      .status-item.info {
        border-color: rgba(59, 130, 246, 0.4);
        background: rgba(59, 130, 246, 0.08);
        color: #1d4ed8;
      }
      code {
        font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
      }
    </style>
  </head>
  <body>
    <!-- Main Content Area -->
    <div class="main-content">
      <header style="text-align: center; margin-bottom: 40px;">
        <h1 style="font-size: 32px; font-weight: 700; color: #1f2937; margin-bottom: 8px;">
          Blue Team Enterprise Copilot
        </h1>
        <p style="color: #6b7280; font-size: 16px;">
          Multi-Agent Expense Orchestration System
        </p>
      </header>

      <div id="role-dashboard" style="margin-top: 20px;">
        <!-- Role-specific content will be rendered here -->
      </div>
    </div>

    <!-- Chat Toggle Button -->
    <button id="chat-toggle-btn" class="chat-toggle-btn">
      <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
      </svg>
    </button>

    <!-- Chat Shell (minimized by default) -->
    <div class="chat-shell minimized" id="chat-shell" style="display: none;">
      <header class="chat-header">
        <div>
          <div class="chat-header-title">Blue Team Enterprise Copilot</div>
          <div class="chat-header-subtitle">Secure expense &amp; policy assistant (local demo)</div>
          <div class="agent-tags">
            <span class="agent-tag">Email agent: notifications &amp; updates</span>
            <span class="agent-tag">Drive agent: policies &amp; documents</span>
            <span class="agent-tag">Expense agent: reimbursements &amp; balances</span>
          </div>
        </div>
        <div class="role-select">
          <span>Logged in as:</span>
          <select id="role-select" disabled style="opacity: 0.7; cursor: not-allowed;">
            <option value="employee">employee</option>
            <option value="admin">admin</option>
            <option value="auditor">auditor</option>
          </select>
          <button id="logout-btn" style="margin-left: 12px; padding: 6px 12px; border-radius: 6px; border: 1px solid rgba(239, 68, 68, 0.3); background: rgba(239, 68, 68, 0.1); color: #b91c1c; cursor: pointer; font-size: 12px;">Logout</button>
        </div>
      </header>
      <main id="chat-log" class="chat-log">
        <div class="message agent">
          <strong>Welcome to Blue Team Copilot</strong><br /><br />
          I can help you with policies, expenses, emails, and administrative tasks.<br /><br />
          Use the action buttons below or type your request.
        </div>
      </main>
      <section class="chat-input">
        <div class="chat-input-inner">
          <textarea id="chat-input" placeholder="Type a question or instruction and press Enter..."></textarea>
          <button id="send-btn">Send</button>
        </div>
        <div class="hint">
          Requests are sent to <code>POST /tasks</code> with the selected role in <code>X-Role</code>. All processing stays local.
        </div>
        <div class="quick-actions">
          <button type="button" id="demo-workflow-btn" style="background: linear-gradient(120deg, #10b981, #14b8a6); color: white; font-weight: 600;">
            Demo Complete Workflow
          </button>
          <button type="button" data-template="Upload a new expense policy that allows travel expenses up to 500 USD per trip with receipt requirement.">
            Upload Policy
          </button>
          <button type="button" data-template="Search for the latest expense reimbursement policy document.">
            Search Policies
          </button>
          <button type="button" data-template="List active expense policies.">
            List Active Policies
          </button>
          <button type="button" data-template="Submit an expense reimbursement for employee emp-001 for 200 USD in the travel category for a taxi from the airport to the client office.">
            Submit Expense
          </button>
          <button type="button" data-template="What is my current expense reimbursement balance for employee emp-001?">
            Check Balance
          </button>
          <button type="button" data-template="Show me the status of my expense reimbursements for employee emp-001.">
            View My Expenses
          </button>
          <button type="button" data-template="Send an email to employee emp-001 confirming their expense reimbursement has been processed.">
            Send Notification
          </button>
          <button type="button" data-template="Deactivate policy policy_v1." data-role="admin">
            Deactivate Policy
          </button>
          <button type="button" data-template="Activate policy policy_v1." data-role="admin">
            Activate Policy
          </button>
          <button type="button" data-template="Show flagged expenses that need manager review." data-role="admin">
            View Flagged Expenses
          </button>
          <button type="button" data-template="Deny expense report rpt-123 due to missing receipt." data-role="admin">
            Deny Expense
          </button>
          <button type="button" id="view-logs-btn" data-role="admin">
            View System Logs
          </button>
          <button type="button" id="auditor-logs-btn" data-role="auditor">
            View Audit Log
          </button>
        </div>
      </section>
      <section class="forms-container">
        <div class="form-section">
          <h3>Manual Expense Form</h3>
          <p>Provide all required fields. Receipts can be pasted as notes or secure links.</p>
          <form id="manual-expense-form" class="form-grid">
            <label>
              Employee ID*
              <input id="manual-employee-id" name="employeeId" required placeholder="e.g., emp-001" />
            </label>
            <label>
              Category*
              <input id="manual-category" name="category" required placeholder="e.g., travel" />
            </label>
            <label>
              Amount*
              <input id="manual-amount" name="amount" type="number" min="0" step="0.01" required placeholder="e.g., 200.00" />
            </label>
            <label>
              Currency*
              <input id="manual-currency" name="currency" required value="USD" placeholder="USD" />
            </label>
            <label>
              Description*
              <textarea id="manual-description" name="description" required placeholder="Reason for the expense"></textarea>
            </label>
            <label>
              Vendor
              <input id="manual-vendor" name="vendor" placeholder="Merchant or vendor name" />
            </label>
            <label>
              Payment Method*
              <select id="manual-payment-method" name="paymentMethod" required>
                <option value="Corporate Card">Corporate Card</option>
                <option value="Personal Card">Personal Card</option>
              </select>
            </label>
            <label>
              Date incurred
              <input id="manual-date-incurred" name="dateIncurred" type="date" />
            </label>
            <label>
              Date submitted
              <input id="manual-date-submitted" name="dateSubmitted" type="date" />
            </label>
            <label>
              Receipt notes / link
              <textarea id="manual-receipt" name="receipt" placeholder="Paste secure file link or receipt text"></textarea>
            </label>
          </form>
          <div class="form-actions">
            <button type="submit" form="manual-expense-form">Submit Expense</button>
          </div>
        </div>
        <div class="form-section">
          <h3>CSV Expense Upload</h3>
          <p>Header must be exactly: <code>TransactionID,EmployeeID,DateIncurred,DateSubmitted,Description,Vendor,PaymentMethod,Currency,Amount,AmountUSD,Category,ReceiptAttached,ReimbursementType</code></p>
          <div class="csv-upload">
            <textarea id="csv-input" placeholder="Paste CSV rows matching the required header..."></textarea>
            <button type="button" id="csv-upload-btn">Upload CSV Batch</button>
          </div>
        </div>
        <div class="status-feed" id="status-feed">
          <h3>Submission Activity</h3>
          <p>Live status for manual form and CSV uploads.</p>
          <div class="status-items" id="status-items"></div>
        </div>
      </section>
    </div>
    <script>
      const logEl = document.getElementById("chat-log");
      const inputEl = document.getElementById("chat-input");
      const sendBtn = document.getElementById("send-btn");
      const roleEl = document.getElementById("role-select");
      const quickActionButtons = document.querySelectorAll(".quick-actions button");
      const viewLogsBtn = document.getElementById("view-logs-btn");
      const auditorLogsBtn = document.getElementById("auditor-logs-btn");
      const demoWorkflowBtn = document.getElementById("demo-workflow-btn");
      const manualForm = document.getElementById("manual-expense-form");
      const csvInput = document.getElementById("csv-input");
      const csvUploadBtn = document.getElementById("csv-upload-btn");
      const manualDateSubmitted = document.getElementById("manual-date-submitted");
      const statusItems = document.getElementById("status-items");
      const sessionId = "webchat-" + Math.random().toString(36).slice(2, 10);
      let currentRole = localStorage.getItem("role") || "employee";
      const storedUsername = localStorage.getItem("username");

      // Check authentication
      if (!localStorage.getItem("auth_token")) {
        window.location.href = "/login";
        return;
      }

      // Ensure all elements exist before using them
      if (!logEl || !inputEl || !sendBtn || !roleEl) {
        console.error("Critical UI elements not found!");
        return;
      }

      // Set role selector to stored role
      if (roleEl && currentRole) {
        roleEl.value = currentRole;
      }

      // Logout handler
      const logoutBtn = document.getElementById("logout-btn");
      if (logoutBtn) {
        logoutBtn.addEventListener("click", () => {
          localStorage.removeItem("auth_token");
          localStorage.removeItem("username");
          localStorage.removeItem("role");
          window.location.href = "/login";
        });
      }

      // Show welcome message with username
      if (storedUsername) {
        appendMessage(`Welcome back, ${storedUsername}. Current role: ${currentRole}`, "meta");
      }

      // Initialize chat as minimized
      const chatShell = document.getElementById("chat-shell");
      const chatToggleBtn = document.getElementById("chat-toggle-btn");
      
      if (chatToggleBtn) {
        chatToggleBtn.addEventListener("click", () => {
          if (chatShell.style.display === "none") {
            chatShell.style.display = "flex";
            chatShell.classList.remove("minimized");
            chatToggleBtn.classList.add("hidden");
          }
        });
      }

      // Close chat button handler
      const closeChatBtn = document.createElement("button");
      closeChatBtn.innerHTML = "×";
      closeChatBtn.style.cssText = "position: absolute; top: 10px; right: 10px; background: transparent; border: none; font-size: 24px; color: #9ca3af; cursor: pointer; z-index: 10;";
      closeChatBtn.onclick = () => {
        chatShell.style.display = "none";
        chatShell.classList.add("minimized");
        chatToggleBtn.classList.remove("hidden");
      };
      document.querySelector(".chat-header").appendChild(closeChatBtn);

      function updateRoleUI(role) {
        currentRole = role;
        // Update header color based on role
        const header = document.querySelector(".chat-header");
        if (header) {
          header.style.borderBottomColor = 
            role === "admin" ? "rgba(239, 68, 68, 0.4)" :
            role === "auditor" ? "rgba(139, 92, 246, 0.4)" :
            "rgba(59, 130, 246, 0.4)";
        }
        // Show/hide role-specific buttons
        const adminButtons = document.querySelectorAll('[data-role="admin"]');
        const auditorButtons = document.querySelectorAll('[data-role="auditor"]');
        adminButtons.forEach(btn => {
          btn.style.display = role === "admin" ? "inline-block" : "none";
        });
        auditorButtons.forEach(btn => {
          btn.style.display = role === "auditor" ? "inline-block" : "none";
        });
        // Update form visibility
        const formsContainer = document.querySelector(".forms-container");
        if (formsContainer) {
          formsContainer.style.display = role === "employee" ? "block" : "none";
        }
      }

      if (manualDateSubmitted && !manualDateSubmitted.value) {
        manualDateSubmitted.value = new Date().toISOString().slice(0, 10);
      }

      // Initialize role UI on page load
      updateRoleUI("employee");

      function pushStatus(message, variant = "info") {
        if (!statusItems) return;
        const item = document.createElement("div");
        item.className = `status-item ${variant}`;
        item.textContent = `${new Date().toLocaleTimeString()} — ${message}`;
        statusItems.appendChild(item);
        statusItems.scrollTop = statusItems.scrollHeight;
      }
      pushStatus("No submissions yet. Manual form or CSV uploads will appear here.", "info");

      function appendMessage(text, role) {
        const div = document.createElement("div");
        div.className = "message " + role;
        // Support HTML formatting for agent responses
        if (role === "agent" && text.includes("<strong>")) {
          div.innerHTML = text.replace(/\n/g, "<br>");
        } else {
          div.textContent = text;
        }
        logEl.appendChild(div);
        logEl.scrollTop = logEl.scrollHeight;
      }

      function summarizeResponse(data, ok, role, fallbackText) {
        // Comprehensive workflow response formatter
        if (!ok) {
          if (data && data.detail) {
            if (data.detail.includes("Role employee not authorized") && role === "employee") {
              return "[ACCESS DENIED] Your request requires admin approval. Employees cannot review or approve their own expenses. An admin will need to complete the process.";
            }
            if (data.detail.includes("Human-in-the-loop approval required")) {
              return "[HITL REQUIRED] This action requires human approval. Please complete the manual approval process before proceeding.";
            }
            return "[ERROR] Request blocked: " + data.detail;
          }
          return "[ERROR] " + (fallbackText || "Unknown server error");
        }

        // Check for comprehensive result with agent details
        if (data && data.result && data.result.summary) {
          const summary = data.result.summary;
          let response = "[SUCCESS] Request processed successfully\n\n";
          let agentActions = [];

          // Expense Agent summary
          if (summary.expense_agent) {
            const exp = summary.expense_agent;
            const status = exp.status || "unknown";
            
            if (status.includes("paid") || status.includes("processed")) {
              response += "<strong>Expense Reimbursement</strong>\n";
              response += "Status: Approved and paid\n";
              
              if (exp.details && exp.details.length > 0) {
                exp.details.forEach((detail) => {
                  const output = detail.output || {};
                  if (output.report_id) {
                    response += `Report ID: ${output.report_id}\n`;
                  }
                  if (output.balance !== undefined) {
                    response += `New Balance: $${output.balance.toFixed(2)}\n`;
                  }
                });
              }
              agentActions.push("Expense Agent: Processed reimbursement");
            } else if (status.includes("submitted")) {
              response += "<strong>Expense Submitted</strong>\n";
              response += "Your expense has been submitted for review\n";
              agentActions.push("Expense Agent: Created expense report");
            } else if (status.includes("flagged")) {
              response += "<strong>Expense Flagged</strong>\n";
              response += "This expense requires manager review\n";
              response += "Reason: Amount exceeds policy limits\n";
              agentActions.push("Expense Agent: Flagged for review");
            } else {
              response += `<strong>Expense Status:</strong> ${status}\n`;
              agentActions.push(`Expense Agent: ${status}`);
            }
          }

          // Drive Agent summary
          if (summary.drive_agent) {
            const drive = summary.drive_agent;
            const status = drive.status || "unknown";
            
            if (status.includes("uploaded")) {
              response += "\n<strong>Policy Upload</strong>\n";
              response += "Policy successfully uploaded and indexed\n";
              agentActions.push("Drive Agent: Policy stored");
            } else if (status.includes("found") || drive.details) {
              const docCount = drive.details ? drive.details.length : 0;
              response += `\n<strong>Policy Search</strong>\n`;
              response += `Found ${docCount} policy document(s)\n`;
              agentActions.push(`Drive Agent: Retrieved ${docCount} documents`);
            }
          }

          // Email Agent summary
          if (summary.email_agent) {
            const email = summary.email_agent;
            const status = email.status || "unknown";
            
            if (status.includes("sent")) {
              response += "\n<strong>Email Notification</strong>\n";
              response += "Confirmation email sent to employee\n";
              agentActions.push("Email Agent: Notification sent");
            }
          }

          // Sheets Agent summary
          if (summary.sheets_agent) {
            response += "\n<strong>Audit Log</strong>\n";
            response += "Activity recorded in system logs\n";
            agentActions.push("Sheets Agent: Logged transaction");
          }

          // Add agent execution summary
          if (agentActions.length > 0) {
            response += "\n<em>Agent trace: " + agentActions.join(" | ") + "</em>";
          }

          return response;
        }

        // Simple status responses
        if (data && data.status === "ok") {
          if (data.ingested) {
            return "[SUCCESS] Policy upload completed. Ingested " + data.ingested + " document(s).";
          }
          return "[SUCCESS] Request completed successfully.";
        }

        // Fallback for other responses
        if (data && data.result && data.result.summary) {
          const parts = [];
          for (const [tool, info] of Object.entries(data.result.summary)) {
            parts.push(tool + ": " + (info.status || "ok"));
          }
          return "[SUCCESS] Request processed\n" + parts.join("\n");
        }

        return "[SUCCESS] Request processed. Check status panel for details.";
      }

      async function executeTask(taskText, role, extraData = {}) {
        const payload = {
          task: taskText,
          data: { session_id: sessionId, ...extraData }
        };
        const token = localStorage.getItem("auth_token");
        const actualRole = localStorage.getItem("role") || role || "employee";
        let response;
        try {
          const headers = {
            "Content-Type": "application/json",
            "X-Role": actualRole
          };
          if (token) {
            headers["Authorization"] = `Bearer ${token}`;
          }
          response = await fetch("/tasks", {
            method: "POST",
            headers: headers,
            body: JSON.stringify(payload)
          });
        } catch (err) {
          return { reply: "Network error: " + err, ok: false };
        }
        const rawText = await response.text();
        let json = null;
        try {
          json = rawText ? JSON.parse(rawText) : null;
        } catch {
          json = null;
        }
        const reply = summarizeResponse(json, response.ok, actualRole, rawText);
        return { reply, data: json, ok: response.ok, raw: rawText };
      }

      async function sendMessage() {
        const text = inputEl.value.trim();
        if (!text) return;
        appendMessage(text, "user");
        inputEl.value = "";

        // Lightweight chat-bot behavior for very short greetings or vague input
        const lower = text.toLowerCase();
        if (
          text.length < 40 &&
          (lower === "hi" ||
            lower === "hello" ||
            lower === "hey" ||
            lower.startsWith("hi ") ||
            lower.startsWith("hello ") ||
            lower.includes("how are you"))
        ) {
          appendMessage(
            "Hi! I'm your Blue Team copilot. You can ask me to upload policies, submit expenses, or check reimbursement status.",
            "agent"
          );
          return;
        }

        const role = localStorage.getItem("role") || currentRole || "employee";
        sendBtn.disabled = true;

        try {
          const result = await executeTask(text, role, {});
          appendMessage(result.reply, "agent");
        } catch (err) {
          appendMessage("Network error: " + err, "agent");
        } finally {
          sendBtn.disabled = false;
        }
      }

      sendBtn.addEventListener("click", sendMessage);
      inputEl.addEventListener("keydown", (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
          e.preventDefault();
          sendMessage();
        }
      });
      // Demo Workflow Button - Simulates complete workflow
      if (demoWorkflowBtn) {
        demoWorkflowBtn.addEventListener("click", async () => {
          const userRole = localStorage.getItem("role") || currentRole;
          if (userRole === "employee") {
            appendMessage("Starting complete workflow demonstration...", "meta");
            pushStatus("Demo: Starting workflow", "info");
            
            // Step 1: Check initial balance
            appendMessage("Step 1: Checking current balance...", "user");
            pushStatus("Demo: Checking balance", "info");
            await new Promise(resolve => setTimeout(resolve, 500));
            appendMessage("Current balance: $1200.00 (emp-001)", "agent");
            
            // Step 2: Submit expense
            await new Promise(resolve => setTimeout(resolve, 800));
            appendMessage("Step 2: Submitting expense reimbursement...", "user");
            pushStatus("Demo: Submitting expense", "info");
            const expenseRequest = "Submit an expense reimbursement for employee emp-001 for 200 USD in the travel category for a taxi from the airport to the client office.";
            const result = await executeTask(expenseRequest, userRole, {
              employee_id: "emp-001",
              category: "travel",
              amount: 200,
              currency: "USD",
              description: "Taxi from airport to client office",
              vendor: "City Taxi",
              payment_method: "Personal Card",
              receipt: "Receipt: City Taxi, $200, 2024-11-17"
            });
            appendMessage(result.reply, "agent");
            pushStatus("Demo: Workflow complete", "success");
            appendMessage("[DEMO COMPLETE] Check the response above for workflow details.", "meta");
          } else if (userRole === "admin") {
            appendMessage("Starting admin workflow demonstration...", "meta");
            pushStatus("Demo: Admin workflow", "info");
            
            // Upload policy
            appendMessage("Step 1: Uploading expense policy...", "user");
            pushStatus("Demo: Uploading policy", "info");
            const policyRequest = "Upload a new expense policy that allows travel expenses up to 500 USD per trip with receipt requirement.";
            const result = await executeTask(policyRequest, userRole, {
              doc_id: "demo_policy_" + Date.now(),
              title: "Demo Expense Policy",
              content: "Travel expenses up to $500 require receipt. Auto-approved under $100.",
              tags: ["policy", "demo"]
            });
            appendMessage(result.reply, "agent");
            
            await new Promise(resolve => setTimeout(resolve, 800));
            appendMessage("Step 2: Viewing flagged expenses...", "user");
            const flaggedResult = await executeTask("Show flagged expenses that need manager review.", userRole, {});
            appendMessage(flaggedResult.reply, "agent");
            
            pushStatus("Demo: Admin workflow complete", "success");
            appendMessage("[DEMO COMPLETE] Admin workflow finished.", "meta");
          } else {
            appendMessage("Demo workflow is available for employee and admin roles.", "meta");
          }
        });
      }

      quickActionButtons.forEach((btn) => {
        btn.addEventListener("click", () => {
          if (btn === viewLogsBtn || btn === auditorLogsBtn || btn === demoWorkflowBtn) {
            return; // handled separately
          }
          const tpl = btn.getAttribute("data-template") || "";
          if (tpl) {
            inputEl.value = tpl;
            inputEl.focus();
          }
        });
      });
      if (viewLogsBtn) {
        viewLogsBtn.addEventListener("click", async () => {
          const userRole = localStorage.getItem("role") || currentRole;
          if (userRole !== "admin") {
            appendMessage("Only admins can view logs. Please login as admin.", "meta");
            return;
          }
          pushStatus("Fetching system logs...", "info");
          try {
            const resp = await fetch("/logs");
            if (!resp.ok) {
              const txt = await resp.text();
              appendMessage("Error fetching logs: " + txt, "agent");
              pushStatus("Failed to fetch logs", "error");
              return;
            }
            const entries = await resp.json();
            if (!Array.isArray(entries) || entries.length === 0) {
              appendMessage("No logs available yet.", "agent");
              pushStatus("No logs found", "info");
              return;
            }
            const last = entries.slice(-5);
            const summaryLines = last.map((e) => {
              const ts = e.timestamp || "";
              const actor = e.actor || "unknown";
              const action = e.action || "event";
              const role = e.role ? ` (role: ${e.role})` : "";
              return `- [${ts}] ${actor}${role}: ${action}`;
            });
            appendMessage("Recent system events:\n" + summaryLines.join("\n"), "agent");
            pushStatus(`Retrieved ${last.length} log entries`, "success");
          } catch (err) {
            appendMessage("Network error while fetching logs: " + err, "agent");
            pushStatus("Error fetching logs", "error");
          }
        });
      }
      if (auditorLogsBtn) {
        auditorLogsBtn.addEventListener("click", async () => {
          const userRole = localStorage.getItem("role") || currentRole;
          if (userRole !== "auditor") {
            appendMessage("Only auditors can fetch audit logs. Please login as auditor.", "meta");
            return;
          }
          pushStatus("Fetching audit logs...", "info");
          try {
            const taskText = "Fetch audit log entries";
            const result = await executeTask(taskText, "auditor", {});
            appendMessage("[Audit Log] " + result.reply, "agent");
            pushStatus("Audit log fetched", result.ok ? "success" : "error");
          } catch (err) {
            appendMessage("Error fetching audit log: " + err, "agent");
            pushStatus("Error fetching audit log", "error");
          }
        });
      }

      if (manualForm) {
        manualForm.addEventListener("submit", async (event) => {
          event.preventDefault();
          if (!manualForm.checkValidity()) {
            manualForm.reportValidity();
            pushStatus("Form validation failed. Please check required fields.", "error");
            return;
          }
          const userRole = localStorage.getItem("role") || currentRole;
          if (userRole !== "employee") {
            pushStatus("Only employees can submit expenses. Please login as an employee.", "error");
            appendMessage("Only employees can submit expenses. Please login as an employee.", "meta");
            return;
          }
          const employeeId = document.getElementById("manual-employee-id").value.trim();
          const category = document.getElementById("manual-category").value.trim();
          const amount = document.getElementById("manual-amount").value.trim();
          const currency = document.getElementById("manual-currency").value.trim();
          const description = document.getElementById("manual-description").value.trim();
          const vendor = document.getElementById("manual-vendor").value.trim();
          const paymentMethod = document.getElementById("manual-payment-method").value;
          const dateIncurred = (document.getElementById("manual-date-incurred").value || "").trim();
          const dateSubmitted =
            (document.getElementById("manual-date-submitted").value || new Date().toISOString().slice(0, 10)).trim();
          const receipt = document.getElementById("manual-receipt").value.trim();
          const transactionId = `manual-${Date.now()}`;

          appendMessage(
            `Manual expense submission: ${employeeId} • ${category} • ${amount} ${currency} (${paymentMethod})`,
            "user"
          );
          pushStatus(`Submitting manual expense for ${employeeId} (${category})`, "info");

          try {
            if (receipt) {
              pushStatus("Uploading receipt...", "info");
              const receiptTask = `Upload receipt file for employee ${employeeId} expense ${description}`;
              const receiptData = {
                doc_id: `receipt-${employeeId}-${Date.now()}`,
                title: `Receipt for ${employeeId} (${category})`,
                content: receipt,
                tags: ["receipt", "expense", "manual_form"]
              };
              const receiptResult = await executeTask(receiptTask, currentRole, receiptData);
              appendMessage("[Receipt] " + receiptResult.reply, "agent");
              pushStatus(`Receipt uploaded: ${receiptResult.ok ? "Success" : "Failed"}`, receiptResult.ok ? "success" : "error");
            }

            pushStatus("Submitting expense reimbursement...", "info");
            const expenseTask = `Submit expense reimbursement for employee ${employeeId} amount ${amount} ${currency} in category ${category} paid via ${paymentMethod}. Description: ${description}. Vendor: ${vendor ||
              "unspecified"}.`;
            const expenseData = {
              employee_id: employeeId,
              category,
              amount: Number(amount),
              currency,
              description,
              vendor,
              payment_method: paymentMethod,
              source: "manual_form",
              receipt,
              receipt_attached: receipt ? "Y" : "N",
              reimbursement_type: "employee",
              transaction_id: transactionId,
              date_incurred: dateIncurred,
              date_submitted: dateSubmitted
            };
            const expenseResult = await executeTask(expenseTask, currentRole, expenseData);
            appendMessage("[Expense] " + expenseResult.reply, "agent");
            if (expenseResult.ok) {
              pushStatus(`Expense submitted successfully: ${transactionId}`, "success");
            } else {
              pushStatus(`Expense submission failed: ${expenseResult.reply}`, "error");
            }
          } catch (err) {
            const errMsg = err.message || String(err);
            pushStatus(`Error: ${errMsg}`, "error");
            appendMessage("Error submitting expense: " + errMsg, "agent");
          }
        });
      }

      function parseCsvInput(text) {
        const lines = text
          .split(/\r?\n/)
          .map((line) => line.trim())
          .filter((line) => line.length > 0);
        if (!lines.length) {
          throw new Error("CSV data is empty.");
        }
        const headerLine = lines.shift();
        const expectedHeaders = [
          "TransactionID",
          "EmployeeID",
          "DateIncurred",
          "DateSubmitted",
          "Description",
          "Vendor",
          "PaymentMethod",
          "Currency",
          "Amount",
          "AmountUSD",
          "Category",
          "ReceiptAttached",
          "ReimbursementType"
        ];
        const normalized = headerLine
          .split(",")
          .map((h) => h.trim().replace(/\s+/g, ""));
        const expectedNormalized = expectedHeaders.map((h) => h.replace(/\s+/g, ""));
        const headerMismatch =
          normalized.length !== expectedNormalized.length ||
          normalized.some((h, idx) => h !== expectedNormalized[idx]);
        if (headerMismatch) {
          throw new Error("CSV header must match exactly: " + expectedHeaders.join(","));
        }
        return lines.map((line, rowIdx) => {
          const values = line.split(",").map((v) => v.trim());
          if (values.length !== expectedHeaders.length) {
            throw new Error(`Row ${rowIdx + 2} does not have ${expectedHeaders.length} columns.`);
          }
          const row = {};
          expectedHeaders.forEach((key, idx) => {
            row[key] = values[idx] ?? "";
          });
          return row;
        });
      }

      if (csvUploadBtn) {
        csvUploadBtn.addEventListener("click", async () => {
          const userRole = localStorage.getItem("role") || currentRole;
          if (userRole !== "employee") {
            appendMessage("Only employees can upload CSV expenses. Please login as an employee.", "meta");
            return;
          }
          const csvText = (csvInput.value || "").trim();
          if (!csvText) {
            appendMessage("Paste CSV data before uploading.", "meta");
            return;
          }
          appendMessage("Processing CSV expense upload...", "user");
          pushStatus("CSV upload started…", "info");
          try {
            const rows = parseCsvInput(csvText);
            pushStatus(`Parsed ${rows.length} expense row(s) from CSV.`, "info");
            const uploadTask = "Upload CSV expense batch document for expenses";
            const uploadData = {
              doc_id: `csv-${Date.now()}`,
              title: `Expense CSV ${new Date().toISOString()}`,
              content: csvText,
              tags: ["expense", "csv", "batch"]
            };
            const uploadResult = await executeTask(uploadTask, currentRole, uploadData);
            appendMessage("[CSV Upload] " + uploadResult.reply, "agent");
            pushStatus(`CSV document stored: ${uploadResult.ok ? "Success" : "Failed"}`, uploadResult.ok ? "success" : "error");
            let successCount = 0;
            let errorCount = 0;
            for (const row of rows) {
              try {
                pushStatus(`Processing row: ${row.TransactionID}...`, "info");
                const taskText = `Submit expense reimbursement from CSV transaction ${row.TransactionID} for employee ${row.EmployeeID} amount ${row.Amount} ${row.Currency} category ${row.Category}.`;
                const extraData = {
                  employee_id: row.EmployeeID,
                  category: row.Category,
                  amount: Number(row.Amount),
                  currency: row.Currency,
                  description: row.Description,
                  vendor: row.Vendor,
                  payment_method: row.PaymentMethod,
                  reimbursement_type: row.ReimbursementType || "employee",
                  receipt_attached: row.ReceiptAttached,
                  transaction_id: row.TransactionID,
                  date_incurred: row.DateIncurred,
                  date_submitted: row.DateSubmitted,
                  source: "csv_upload",
                  amount_usd: row.AmountUSD
                };
                const result = await executeTask(taskText, currentRole, extraData);
                appendMessage(`[CSV:${row.TransactionID}] ` + result.reply, "agent");
                if (result.ok) {
                  successCount++;
                  pushStatus(`Row ${row.TransactionID}: Submitted`, "success");
                } else {
                  errorCount++;
                  pushStatus(`Row ${row.TransactionID}: Failed`, "error");
                }
              } catch (rowErr) {
                errorCount++;
                const errMsg = rowErr.message || String(rowErr);
                pushStatus(`Row ${row.TransactionID}: Error`, "error");
                appendMessage(`[CSV:${row.TransactionID}] Error: ${errMsg}`, "agent");
              }
            }
            appendMessage(`CSV processing complete. ${successCount} succeeded, ${errorCount} failed.`, "agent");
            pushStatus(`CSV batch complete: ${successCount} succeeded, ${errorCount} failed.`, successCount > 0 ? "success" : "error");
          } catch (err) {
            const errMsg = err.message || String(err);
            pushStatus(`CSV error: ${errMsg}`, "error");
            appendMessage("CSV error: " + errMsg, "agent");
          }
        });
      }
      // Role selector is disabled - role is determined by login
      // No change handler needed

      // Render role-based dashboard content
      function renderRoleDashboard(role) {
        const dashboard = document.getElementById("role-dashboard");
        if (!dashboard) return;

        if (role === "employee") {
          dashboard.innerHTML = `
            <div style="max-width: 1200px; margin: 0 auto;">
              <div style="display: grid; grid-template-columns: 2fr 1fr; gap: 24px; margin-bottom: 24px;">
                <div style="background: white; padding: 24px; border-radius: 12px; border: 1px solid #e5e7eb;">
                  <h2 style="font-size: 20px; font-weight: 600; margin-bottom: 16px; color: #1f2937;">Submit Expense Report</h2>
                  <p style="font-size: 14px; color: #6b7280; margin-bottom: 16px;">Active User: Alice Employee (emp-001) | Current Balance: <span style="font-family: monospace; font-size: 18px; color: #4f46e5;">$1200.00</span></p>
                  <p style="font-size: 14px; color: #9ca3af; margin-top: 16px;">Use the manual form in the chat assistant or click the chat icon to submit expenses.</p>
                </div>
                <div style="background: white; padding: 24px; border-radius: 12px; border: 1px solid #e5e7eb;">
                  <h2 style="font-size: 20px; font-weight: 600; margin-bottom: 16px; color: #1f2937;">Quick Actions</h2>
                  <div style="display: flex; flex-direction: column; gap: 12px;">
                    <button onclick="openChatWithTemplate('Submit expense')" style="padding: 12px; background: #4f46e5; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: 500;">Submit New Expense</button>
                    <button onclick="openChatWithTemplate('Check balance')" style="padding: 12px; background: #10b981; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: 500;">Check Balance</button>
                    <button onclick="openChatWithTemplate('View expenses')" style="padding: 12px; background: #3b82f6; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: 500;">View My Expenses</button>
                  </div>
                </div>
              </div>
            </div>
          `;
        } else if (role === "admin") {
          dashboard.innerHTML = `
            <div style="max-width: 1200px; margin: 0 auto;">
              <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 24px;">
                <div style="background: white; padding: 24px; border-radius: 12px; border: 1px solid #e5e7eb;">
                  <h2 style="font-size: 20px; font-weight: 600; margin-bottom: 16px; color: #1f2937;">Policy Management</h2>
                  <div style="display: flex; flex-direction: column; gap: 12px;">
                    <button onclick="openChatWithTemplate('Upload policy')" style="padding: 12px; background: #4f46e5; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: 500;">Upload New Policy</button>
                    <button onclick="openChatWithTemplate('List policies')" style="padding: 12px; background: #3b82f6; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: 500;">List All Policies</button>
                    <button onclick="openChatWithTemplate('Deactivate policy')" style="padding: 12px; background: #ef4444; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: 500;">Deactivate Policy</button>
                  </div>
                </div>
                <div style="background: white; padding: 24px; border-radius: 12px; border: 1px solid #e5e7eb;">
                  <h2 style="font-size: 20px; font-weight: 600; margin-bottom: 16px; color: #1f2937;">Expense Review</h2>
                  <div style="display: flex; flex-direction: column; gap: 12px;">
                    <button onclick="openChatWithTemplate('View flagged')" style="padding: 12px; background: #f59e0b; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: 500;">View Flagged Expenses</button>
                    <button onclick="openChatWithTemplate('View logs')" style="padding: 12px; background: #6366f1; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: 500;">View System Logs</button>
                    <button onclick="openChatWithTemplate('Deny expense')" style="padding: 12px; background: #dc2626; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: 500;">Deny Expense</button>
                  </div>
                </div>
              </div>
            </div>
          `;
        } else if (role === "auditor") {
          dashboard.innerHTML = `
            <div style="max-width: 1200px; margin: 0 auto;">
              <div style="display: grid; grid-template-columns: 1fr 2fr; gap: 24px;">
                <div style="background: white; padding: 24px; border-radius: 12px; border: 1px solid #e5e7eb;">
                  <h2 style="font-size: 20px; font-weight: 600; margin-bottom: 16px; color: #1f2937;">Employee Profiles</h2>
                  <div style="display: flex; flex-direction: column; gap: 12px;">
                    <div style="padding: 12px; border: 1px solid #e5e7eb; border-radius: 8px;">
                      <p style="font-weight: 600; color: #1f2937;">Alice Employee <span style="font-size: 12px; color: #9ca3af;">(emp-001)</span></p>
                      <p style="font-size: 14px; color: #6b7280;">Bank: 123456789</p>
                      <p style="font-size: 16px; font-weight: 600; color: #4f46e5; margin-top: 4px;">Balance: $1200.00</p>
                    </div>
                    <div style="padding: 12px; border: 1px solid #e5e7eb; border-radius: 8px;">
                      <p style="font-weight: 600; color: #1f2937;">Bob Johnson <span style="font-size: 12px; color: #9ca3af;">(emp-002)</span></p>
                      <p style="font-size: 14px; color: #6b7280;">Bank: 987654321</p>
                      <p style="font-size: 16px; font-weight: 600; color: #4f46e5; margin-top: 4px;">Balance: $500.00</p>
                    </div>
                  </div>
                </div>
                <div style="background: white; padding: 24px; border-radius: 12px; border: 1px solid #e5e7eb;">
                  <h2 style="font-size: 20px; font-weight: 600; margin-bottom: 16px; color: #1f2937;">Audit Actions</h2>
                  <div style="display: flex; flex-direction: column; gap: 12px;">
                    <button onclick="openChatWithTemplate('Fetch audit log')" style="padding: 12px; background: #8b5cf6; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: 500;">Fetch Audit Log</button>
                    <button onclick="openChatWithTemplate('View all reports')" style="padding: 12px; background: #3b82f6; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: 500;">View All Reports</button>
                  </div>
                  <p style="font-size: 14px; color: #6b7280; margin-top: 16px;">Use the chat assistant to view detailed audit trails and expense report traces.</p>
                </div>
              </div>
            </div>
          `;
        }
      }

      // Helper function to open chat with template
      window.openChatWithTemplate = function(action) {
        const chatShell = document.getElementById("chat-shell");
        const chatToggleBtn = document.getElementById("chat-toggle-btn");
        const inputEl = document.getElementById("chat-input");
        
        if (chatShell.style.display === "none") {
          chatShell.style.display = "flex";
          chatShell.classList.remove("minimized");
          chatToggleBtn.classList.add("hidden");
        }

        const templates = {
          'Submit expense': "Submit an expense reimbursement for employee emp-001 for 200 USD in the travel category for a taxi from the airport to the client office.",
          'Check balance': "What is my current expense reimbursement balance for employee emp-001?",
          'View expenses': "Show me the status of my expense reimbursements for employee emp-001.",
          'Upload policy': "Upload a new expense policy that allows travel expenses up to 500 USD per trip with receipt requirement.",
          'List policies': "List active expense policies.",
          'Deactivate policy': "Deactivate policy policy_v1.",
          'View flagged': "Show flagged expenses that need manager review.",
          'View logs': "View system logs",
          'Deny expense': "Deny expense report rpt-123 due to missing receipt.",
          'Fetch audit log': "Fetch audit log entries",
          'View all reports': "Show me all submitted expense reports."
        };

        if (templates[action]) {
          inputEl.value = templates[action];
          inputEl.focus();
        }
      };

      // Initialize dashboard based on current role
      const initialRole = localStorage.getItem("role") || "employee";
      renderRoleDashboard(initialRole);
    </script>
  </body>
</html>
"""


@app.get("/login", response_class=HTMLResponse)
async def login_page(_: Request) -> HTMLResponse:
    """Serve the login page."""
    return HTMLResponse(content=LOGIN_HTML)


@app.get("/", response_class=HTMLResponse)
async def chat_ui(_: Request) -> HTMLResponse:
    """Serve a minimal web chat UI for interacting with the copilot."""
    return HTMLResponse(content=CHAT_HTML)


# Agent Ecosystem Defense: Signed communication between agents
AGENT_SIG_SECRET = "AGENT_SIG_SECRET"

# MCP Server configuration for Model Context Protocol
MCP_URL = "http://localhost:8001"
MCP_SIG_SECRET = "MOCK_MCP_SECRET"

# Admin Authentication: API Key for admin role protection
ADMIN_SECRET_KEY = "SECRET_123_ADMIN_KEY"


# Authentication Dependency: Admin Role Verification
def verify_admin_token(x_admin_token: str = Header(None)) -> bool:
    """
    Verify admin token from X-Admin-Token header.
    
    Returns True if valid admin token provided, False otherwise.
    Used for Authentication & Identity protection (MAESTRO Security).
    """
    if x_admin_token == ADMIN_SECRET_KEY:
        logger.info("[Auth] Valid admin token provided")
        return True
    else:
        if x_admin_token is not None:
            logger.warning(f"[Auth] Invalid admin token attempt: {x_admin_token[:10]}...")
        return False


# RBAC Models
class TaskRequest(BaseModel):
    task: str
    data: dict = {}
    user_role: str = 'employee'


class EmailSendRequest(BaseModel):
    to: str
    subject: str
    body: str


@app.post("/agents/email/send")
async def send_agent_email(
    req: EmailSendRequest,
    signature: str = Header(None)
) -> dict:
    """
    Specialized agent endpoint for sending emails.
    
    Implements Agent Ecosystem defense from MAESTRO specification:
    - Requires signed communication between agents
    - Validates signature header against mock secret
    
    Returns 403 if signature is missing or invalid.
    Returns 200 with success message if valid.
    """
    # Check for signature in header
    if signature is None or signature != AGENT_SIG_SECRET:
        raise HTTPException(
            status_code=403,
            detail="Unauthorized: Missing or invalid agent signature"
        )
    
    # Signature is valid - process the email send request
    from pathlib import Path
    from datetime import datetime, timezone
    import json
    import os
    
    # Log the successful action to events.jsonl
    log_dir = Path(os.getenv("LOG_DIR", "./logs")).resolve()
    log_dir.mkdir(parents=True, exist_ok=True)
    events_path = log_dir / "events.jsonl"
    
    log_entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "actor": "agent",
        "action": "agent_email_send",
        "to": req.to,
        "subject": req.subject,
        "authenticated": True
    }
    
    with events_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry) + "\n")
    
    # Return success response
    return {
        "status": "success",
        "message": f"Email sent successfully to {req.to}",
        "subject": req.subject
    }


# MCP Integration: Expense Agent Inbox Checking
@app.post("/agents/expense/check_inbox")
async def check_expense_agent_inbox() -> dict:
    """
    Check MCP inbox for ExpenseAgent and process pending messages.
    
    This endpoint simulates the Expense Agent running as a separate service
    that periodically checks the MCP message bus for incoming tasks.
    
    Implements Model Context Protocol with protocol-based message routing.
    
    Returns:
        Summary of processed messages and results
    """
    from pathlib import Path
    from datetime import datetime, timezone
    import json
    import os
    
    # Import Agent to access ExpenseAgent
    from .agent import Agent
    
    # Initialize agent (which includes ExpenseAgent)
    agent = Agent()
    
    try:
        # Check MCP inbox for ExpenseAgent
        logger.info("[MCP Inbox] Checking inbox for ExpenseAgent")
        
        response = requests.get(
            f"{MCP_URL}/inbox/ExpenseAgent",
            timeout=5
        )
        
        if response.status_code != 200:
            return {
                "status": "error",
                "message": f"Failed to check inbox: {response.status_code}"
            }
        
        inbox_data = response.json()
        messages = inbox_data.get('messages', [])
        
        logger.info(f"[MCP Inbox] Retrieved {len(messages)} message(s)")
        
        if not messages:
            return {
                "status": "ok",
                "message": "No pending messages in inbox",
                "message_count": 0,
                "results": []
            }
        
        # Process each message
        processed_results = []
        
        for message in messages:
            msg_id = message.get('id')
            protocol = message.get('protocol')
            task_id = message.get('task_id')
            payload = message.get('payload', {})
            
            logger.info(
                f"[MCP Inbox] Processing message {msg_id} "
                f"(Protocol: {protocol}, Task: {task_id})"
            )
            
            # Extract payload data
            employee_id = payload.get('employee_id', 'unknown')
            amount = payload.get('amount', 0.0)
            request_content = payload.get('request_content', '')
            
            # Process via ExpenseAgent
            try:
                expense_result = agent.expense_agent.process_report(
                    employee_id=employee_id,
                    expense_amount=amount,
                    request_content=request_content
                )
                
                logger.info(
                    f"[MCP Inbox] Processed message {msg_id}: "
                    f"Decision={expense_result.get('decision')}"
                )
                
                processed_results.append({
                    "message_id": msg_id,
                    "task_id": task_id,
                    "protocol": protocol,
                    "status": "processed",
                    "result": expense_result
                })
                
            except Exception as e:
                logger.error(f"[MCP Inbox] Error processing message {msg_id}: {e}")
                processed_results.append({
                    "message_id": msg_id,
                    "task_id": task_id,
                    "protocol": protocol,
                    "status": "error",
                    "error": str(e)
                })
        
        # Log inbox check completion
        log_dir = Path(os.getenv("LOG_DIR", "./logs")).resolve()
        log_dir.mkdir(parents=True, exist_ok=True)
        events_path = log_dir / "events.jsonl"
        
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "actor": "expense_agent",
            "action": "mcp_inbox_checked",
            "message_count": len(messages),
            "processed_count": len([r for r in processed_results if r['status'] == 'processed'])
        }
        
        with events_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry) + "\n")
        
        return {
            "status": "ok",
            "message": f"Processed {len(processed_results)} message(s) from inbox",
            "message_count": len(messages),
            "protocols_used": inbox_data.get('protocols', []),
            "results": processed_results
        }
        
    except requests.exceptions.ConnectionError:
        logger.error("[MCP Inbox] MCP server not available")
        return {
            "status": "error",
            "message": "MCP server not available"
        }
    except Exception as e:
        logger.error(f"[MCP Inbox] Unexpected error: {e}")
        return {
            "status": "error",
            "message": f"Unexpected error: {str(e)}"
        }


# Red Team Testing
@app.post("/tests/rt-full")
async def run_rt_full() -> dict:
    """
    Execute full Red Team test suite.
    
    Runs all security tests:
    - RT-02: Denylisted Action
    - RT-03: RBAC Bypass
    - RT-04: High-Value Anomaly
    - RT-05: Data Provenance
    
    Results written to redteam/results/RT-FULL/rt-full-results.json
    """
    from pathlib import Path
    from datetime import datetime, timezone
    import json
    import os
    
    # Import Red Team suite and required classes
    from .agent import Agent
    from .retriever import Retriever
    from .red_team_suite import run_full_suite
    
    # Initialize agent and retriever
    agent = Agent()
    retriever = Retriever()
    
    # Run the full test suite
    results = run_full_suite(agent, retriever)
    
    # Ensure results directory exists
    results_dir = Path("./redteam/results/RT-FULL").resolve()
    results_dir.mkdir(parents=True, exist_ok=True)
    
    # Write results to file
    results_file = results_dir / "rt-full-results.json"
    with results_file.open("w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    
    # Log high-level event to events.jsonl
    log_dir = Path(os.getenv("LOG_DIR", "./logs")).resolve()
    log_dir.mkdir(parents=True, exist_ok=True)
    events_path = log_dir / "events.jsonl"
    
    log_entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "actor": "redteam",
        "action": "rt_full_suite_executed",
        "summary": results["summary"],
        "results_file": str(results_file)
    }
    
    with events_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry) + "\n")
    
    return {
        "status": "ok",
        "message": "Full Red Team suite executed",
        "results": results,
        "results_file": str(results_file)
    }


# RBAC: Role-Based Access Control for /tasks endpoint
@app.post("/tasks")
async def submit_task(
    req: TaskRequest,
    is_admin: bool = Depends(verify_admin_token)
) -> dict:
    """
    Submit a task with Authentication & RBAC enforcement.
    
    Implements Security Controls:
    - Authentication: Verifies X-Admin-Token header for admin actions
    - RBAC: Checks admin authorization for upload operations
    - Identity: Validates employee_id in agent workflow
    - Logs all task submissions and access attempts
    """
    from pathlib import Path
    from datetime import datetime, timezone
    import json
    import os
    
    # Authentication & RBAC Check: Only authenticated admin can upload
    if req.task.lower().startswith('upload'):
        if not is_admin:
            # Log unauthorized access attempt (missing/invalid admin token)
            log_dir = Path(os.getenv("LOG_DIR", "./logs")).resolve()
            log_dir.mkdir(parents=True, exist_ok=True)
            events_path = log_dir / "events.jsonl"
            
            log_entry = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "actor": "authentication",
                "action": "access_denied",
                "user_role": req.user_role,
                "task": req.task,
                "reason": "Missing or invalid admin authentication token",
                "severity": "HIGH"
            }
            
            with events_path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry) + "\n")
            
            raise HTTPException(
                status_code=401,
                detail="Unauthorized: Invalid or missing Admin Token. Provide X-Admin-Token header."
            )
    
    # Log authorized task submission
    log_dir = Path(os.getenv("LOG_DIR", "./logs")).resolve()
    log_dir.mkdir(parents=True, exist_ok=True)
    events_path = log_dir / "events.jsonl"
    
    log_entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "actor": "user",
        "action": "task_submitted",
        "user_role": req.user_role,
        "task": req.task,
        "authenticated_admin": is_admin,
        "authorized": True
    }
    
    with events_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry) + "\n")
    
    # Import and use Agent to handle the task
    from .agent import Agent
    
    agent = Agent()
    result = agent.handle_task(req.task, req.data)
    
    return {
        "status": "ok",
        "user_role": req.user_role,
        "authenticated_admin": is_admin,
        "result": result
    }


