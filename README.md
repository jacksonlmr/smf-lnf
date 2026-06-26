# Lost and Found Logger

Lightweight web-app to scan physical lost and found forms, and transcribe the data into a google sheet for further processing. 

---

## Development Setup Guide

### Prerequisites
Before starting, ensure you have the following installed by following their official documentation guides:
* **WSL 2 (Windows Subsystem for Linux):** Follow the [Microsoft WSL Installation Guide](https://learn.microsoft.com/en-us/windows/wsl/install) to install WSL and a Linux distribution (This project was initially developed using Ubuntu 26.04).
* **Docker Desktop:** Follow the [Docker Desktop for Windows Guide](https://docs.docker.com/desktop/setup/install/windows-install/) and ensure the WSL 2 backend is enabled.
* **Visual Studio Code:** Follow the [VS Code Installation Guide](https://code.visualstudio.com/docs/setup/windows) and install both the **[WSL](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-wsl)** extension and the **[Dev Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)** extension from the marketplace.
* **Gemini API Key:** Get a valid API key through https://aistudio.google.com.

---

### 1. Configure Docker Desktop WSL Integration
1. Open Docker Desktop and click the **Settings** (gear) icon.
2. Navigate to **General** and verify that **Use the WSL 2 based engine** is checked.
3. Navigate to **Resources > WSL Integration**.
4. Check **Enable integration with my default WSL distro**, and toggle the switch under **Enable integration with additional distros** for your installed Ubuntu distribution to the "on" position.
5. Click **Apply & restart**.

### 2. Clone the Project into the WSL Filesystem
*(Note: You must clone into the native Linux filesystem, not the Windows mounted `C:\` drive)*
1. Open your **Ubuntu** terminal application from the Windows Start menu.
2. Clone the repository in your desired directory
   ```bash
   git clone https://github.com/jacksonlmr/smf-lnf.git smf-lnf-app
   ```
3. Navigate into the project folder:
   ```bash
   cd smf-lnf-app
   ```
### 3. Environment Setup

This application requires secure API keys to function. You must configure these variables locally before building the container.

1. In the root directory of the project, create a new file named `.env`.
2. Add the following variables to the file: 

```
GEMINI_API_KEY="your_actual_api_key_here"
GEMINI_MODEL="gemini-3.5-flash" 
```

### 4. Open in VS Code and Rebuild in Container
1. From the Ubuntu terminal, within the project directory, execute:
   ```bash
   code .
   ```
2. Press `F1` in VS Code to open the Command Palette.
3. Type and select: **Dev Containers: Reopen in Container**.
4. Wait for Docker to complete building the image using your `Dockerfile` and `devcontainer.json`.

### 5. Run the Application
1. Open the VS Code integrated terminal (`Ctrl+~`).
2. Start the Streamlit server:
   ```bash
   streamlit run app.py
   ```
3. Open your web browser on Windows and navigate to `http://localhost:8501`.



