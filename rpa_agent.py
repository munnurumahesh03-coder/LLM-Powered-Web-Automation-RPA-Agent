import os
import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from groq import Groq
from pymongo import MongoClient

print("🤖 RPA Agent Waking Up...")

# 1. Configure Headless Browser
chrome_options = Options()
chrome_options.add_argument('--headless=new')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(options=chrome_options)

# 2. Scrape the Website
mock_url = "data:text/html,<html><body><h1>HextGen MedTech - Public Provider Directory</h1><div class='provider'><p>Dr. Sarah Jenkins - Cardiology</p><p>Contact: 555-0198</p><p>Available: Mon-Wed</p></div><div class='provider'><p>Dr. Marcus Chen, Neurology</p><p>Phone: (555) 847-3321</p><p>Notes: Not accepting new patients.</p></div><div class='provider'><p>Pediatrics: Dr. Emily Ross</p><p>Call 555-0024 for appointments.</p></div></body></html>"
driver.get(mock_url)
time.sleep(2)
raw_text = driver.find_element(By.TAG_NAME, "body").text
driver.quit()
print("✅ Data Scraped!")

# 3. Process with LLM
client = Groq(api_key=os.environ["GROQ_API_KEY"])
prompt = f"Extract doctors info as strict JSON array with keys: name, specialty, phone, notes. RAW TEXT:\n{raw_text}\nOUTPUT ONLY VALID JSON."
response = client.chat.completions.create(
    model="openai/gpt-oss-120b",
    messages=[{"role": "user", "content": prompt}],
    temperature=0
)
structured_data = response.choices[0].message.content.strip()
if structured_data.startswith("```json"): structured_data = structured_data[7:-3].strip()
elif structured_data.startswith("```"): structured_data = structured_data[3:-3].strip()
json_data = json.loads(structured_data)
print("✅ Data Cleaned by AI!")

# 4. Push to MongoDB
mongo_client = MongoClient(os.environ["MONGO_URI"])
db = mongo_client["hextgen_medtech"]
collection = db["providers"]
collection.delete_many({}) # Clear old data for the daily refresh
collection.insert_many(json_data)
print(f"✅ SUCCESS! {len(json_data)} records pushed to MongoDB Atlas!")
