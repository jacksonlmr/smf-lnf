# Lost and Found Logger

Lightweight web-app to scan physical lost and found forms, and transcribe the data into a google sheet for further processing. 

## Prerequisites

Before running this application, ensure you have the following:
* [Docker Desktop](https://www.docker.com/products/docker-desktop/) (or Docker Engine) installed on your machine. 
* A Google Cloud Project with the **Gemini API** enabled.

---

## Google Cloud Setup

You must have a Google Cloud account setup with a Gemini API key to run this app. 

## Step 1: Environment Setup

This application requires secure API keys to function. You must configure these variables locally before building the container.

1. In the root directory of the project, create a new file named `.env`.
2. Add your Gemini API key to the file using the format below. 

**`.env`**
```
GEMINI_API_KEY="your_actual_api_key_here"
```

## Step 2: Build Docker Image

Run the following command: 

```
docker build -t smf-lnf .
```

## Step 3: Run Container

Run the following command: 

```
docker run -p 8501:8501 --env-file .env smf-lnf
```




