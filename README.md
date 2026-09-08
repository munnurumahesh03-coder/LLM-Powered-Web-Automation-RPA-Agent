# 🤖 LLM-Powered Web Automation & RPA Agent

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg )](https://www.python.org/ )
[![Selenium](https://img.shields.io/badge/Selenium-Web_Automation-43B02A.svg )](https://www.selenium.dev/ )
[![MongoDB](https://img.shields.io/badge/MongoDB_Atlas-Cloud_Database-47A248.svg )](https://www.mongodb.com/ )
[![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED.svg )](https://www.docker.com/ )
[![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-CI%2FCD_Cron-2088FF.svg )](https://github.com/features/actions )

## 📌 Overview
This project is an automated **Robotic Process Automation (RPA) and ETL Pipeline**. It utilizes a headless Selenium browser to navigate web directories, extracts unstructured DOM data, and leverages a Large Language Model (Groq Llama-3 120B) to dynamically parse, clean, and structure the data into JSON. The structured data is then securely ingested into a cloud-hosted MongoDB Atlas NoSQL database.

The entire pipeline is deployed as a serverless **Cron Job via GitHub Actions**, ensuring the database is updated automatically without human intervention.

## 🏗️ System Architecture (ETL Pipeline)

1. **Extract (Selenium WebDriver):** A headless Chrome browser boots up in a Linux container, navigates to the target directory (e.g., Wikipedia's Medical Laureates), and extracts the raw, unstructured `<body>` text.
2. **Transform (LLM Parsing):** Traditional web scrapers break when website layouts change. Instead of relying on fragile XPaths, this system passes the raw text to an LLM. Using advanced Prompt Engineering, the AI intelligently identifies the target entities, filters them based on business logic, and formats them into a strict JSON array.
3. **Load (MongoDB Atlas):** The Python script connects to an AWS-hosted MongoDB cluster via `pymongo` and securely pushes the structured JSON data into the designated collection.
4. **Automate (CI/CD):** A GitHub Actions YAML workflow triggers the script to run automatically on a scheduled basis.

## 🧠 Key Engineering Decisions
| Component | Technology | Rationale |
| :--- | :--- | :--- |
| **Web Automation** | Selenium | Capable of rendering JavaScript-heavy pages and bypassing basic anti-bot protections that block standard `requests` libraries. |
| **Data Structuring** | Groq (Llama-3) | Replaces brittle RegEx and XPath rules. The LLM understands context, allowing it to extract data even if the website's HTML structure completely changes. |
| **Database** | MongoDB Atlas | NoSQL document structure is perfectly suited for ingesting dynamic JSON outputs from LLMs. |
| **Deployment** | Docker & GitHub Actions | Containerizing the scraper ensures it runs flawlessly on any cloud server, while GitHub Actions provides free, serverless Cron scheduling. |

## 🐳 Run Locally via Docker (Recommended)
The automation pipeline is fully containerized. You can pull and run the image directly from the GitHub Container Registry. You must pass your API keys as environment variables (`-e`) for the script to authenticate.

```bash
# Pull the latest image
docker pull ghcr.io/munnurumahesh03-coder/llm-powered-web-automation-rpa-agent:latest

# Run the container (Injecting your secret keys)
docker run -e GROQ_API_KEY="your_groq_key" -e MONGO_URI="your_mongodb_connection_string" ghcr.io/munnurumahesh03-coder/llm-powered-web-automation-rpa-agent:latest
```

## 💻 Manual Local Execution
If you wish to run the Python script directly on your machine:

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/LLM-Powered-Web-Automation-RPA-Agent.git
cd LLM-Powered-Web-Automation-RPA-Agent

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set Environment Variables
export GROQ_API_KEY="your_groq_key"
export MONGO_URI="your_mongodb_connection_string"

# 4. Run the Agent
python rpa_agent.py
```
