# SEA App - Deployment Guide

This document outlines the hosting options evaluated for the SEA App and provides step-by-step instructions for deploying the application to the chosen platform: **Streamlit Community Cloud (SCC)**.

## 1. Hosting Comparison: Streamlit Community Cloud vs. Render

When taking a local Python application (specifically a Streamlit app) and making it available on the public internet, two popular Platform-as-a-Service (PaaS) providers were considered.

### Streamlit Community Cloud (SCC)
**SCC** is the native, free hosting platform provided by the creators of Streamlit.
*   **Pros:**
    *   **Simplicity:** Deployment requires zero configuration files (`Dockerfiles`). It links directly to GitHub and deploys automatically.
    *   **Cost:** 100% Free for public GitHub repositories.
    *   **Native Support:** Seamless integration and immediate support for all Streamlit features.
*   **Cons:**
    *   **Sleep Mode:** The application will go to "sleep" after several days of inactivity. The next visitor will experience a 30-60 second spin-up time.
    *   **Resource Limits:** Limited to ~1GB of RAM (plenty for our current physical equations, but a bottleneck for heavy Machine Learning).

### Render.com
**Render** is a generalized cloud hosting provider capable of running arbitrary code, web servers, and databases.
*   **Pros:**
    *   **Full Control:** Complete control over the operating system environment (usually via Docker).
    *   **Scalability:** Allows seamless scaling of CPU and RAM for high-traffic applications (paid tiers).
*   **Cons:**
    *   **Setup Overhead:** Requires configuring build commands (`pip install -r requirements.txt`) and start commands (`streamlit run app.py --server.port $PORT`).
    *   **Free Tier Limits:** The free tier restricts RAM strictly to 512MB and limits uptime to 750 hours/month across all apps. It also spins down inactive apps.

**Decision:** **Streamlit Community Cloud** was chosen as the optimal platform for its frictionless deployment process and perfect alignment with our tech stack.

---

## 2. Preparations for SCC

To deploy successfully on SCC, the platform needs to know two types of dependencies:

1.  **Python Packages:** Extracted into `requirements.txt` (generated via `uv export`). This tells the SCC environment to install libraries like `numpy` and `streamlit`.
2.  **OS Native Packages:** Specified in `packages.txt`. Since we use the Python `graphviz` library to draw the system architecture, the underlying Linux server requires the native `graphviz` C-library to render the graphics.

*Both of these files are included in the root of the `SEA-App` repository.*

---

## 3. How to Deploy (Step-by-Step)

Follow these instructions to push the SEA App live:

1.  **Sign Up / Log In:**
    *   Navigate to [share.streamlit.io](https://share.streamlit.io/).
    *   Log in using your **GitHub account**. Ensure you grant Streamlit permission to read your repositories.
2.  **Create New App:**
    *   Click the **"New app"** button.
    *   Select **"Use existing repo"** (from GitHub).
3.  **Configure Deployment:**
    *   **Repository:** Type `wemor/SEA-App` (or select it from the dropdown).
    *   **Branch:** Select `main`.
    *   **Main file path:** Type `app.py`.
4.  **Deploy:**
    *   Click the large **"Deploy!"** button.
5.  **Baking Process:**
    *   You will see an oven animation. The SCC server is now:
        1. Reading `packages.txt` and installing `graphviz` via `apt-get`.
        2. Reading `requirements.txt` and doing `pip install`.
        3. Starting your application.
    *   This first setup takes about 1-2 minutes.
6.  **Live:**
    *   The application will appear on your screen. You will also get a public URL (e.g., `https://sea-app-wemo.streamlit.app`) that you can share with anyone!

### Continuous Deployment
The deployment is linked to your GitHub repository. Whenever you write new code locally and run `git push`, Streamlit Community Cloud detects the change and automatically updates your live website within seconds.
