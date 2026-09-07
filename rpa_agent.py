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

# 2. Scrape the Directory (Using a realistic Indian Hospital Directory mock)
mock_url = """data:text/html,
<html><body>
<h1>National Hospital Directory - India</h1>
<div class="provider"><p>Dr. Vikram Sharma - Neurology - Delhi</p><p>Contact: 9811122233</p></div>
<div class="provider"><p>Dr. Rajesh Kumar - Cardiology - Mumbai</p><p>Phone: 9876543210</p><p>Experience: 15 Years</p></div>
<div class="provider"><p>Dr. Sneha Patel - Pediatrics - Mumbai</p><p>Contact: 9988776655</p></div>
<div class="provider"><p>Dr. Anil Desai - Cardiology - Mumbai</p><p>Phone: 9123456789</p><p>Available: Mon-Fri</p></div>
<div class="provider"><p>Dr. Priya Reddy - Cardiology - Bangalore</p><p>Phone: 9998887776</p></div>
</body></html>
"""
print("🌐 Navigating to the Directory...")
driver.get(mock_url)
time.sleep(2)
raw_text = driver.find_element(By.TAG_NAME, "body").text
driver.quit()
print("✅ Data Scraped!")

# 3. Process with LLM (THE MUMBAI CARDIOLOGIST FILTER)
client = Groq(api_key=os.environ["GROQ_API_KEY"])
prompt = f"""
Extract doctor information from this text.
CRITICAL FILTER: ONLY extract doctors whose specialty is 'Cardiology' AND who are located in 'Mumbai'. 
Ignore all other doctors (like Delhi doctors, Bangalore doctors, or Pediatricians).
Format as a strict JSON array with keys: 'name', 'specialty', 'location', 'phone'.
RAW TEXT:
{raw_text}
OUTPUT ONLY VALID JSON.
"""
response = client.chat.completions.create(
    model="openai/gpt-oss-120b",
    messages=[{"role": "user", "content": prompt}],
    temperature=0
)
structured_data = response.choices[0].message.content.strip()
if structured_data.startswith("```json"): structured_data = structured_data[7:-3].strip()
elif structured_data.startswith("```"): structured_data = structured_data[3:-3].strip()
json_data = json.loads(structured_data)
print("✅ Data Cleaned and Filtered by AI!")

# 4. Push to MongoDB (NEW COLLECTION)
mongo_client = MongoClient(os.environ["MONGO_URI"])
db = mongo_client["hextgen_medtech"]

# THIS CREATES THE BRAND NEW FOLDER!
collection = db["mumbai_cardiologists"] 

collection.delete_many({}) # Clears old data in this specific folder
if len(json_data) > 0:
    collection.insert_many(json_data)
    print(f"✅ SUCCESS! {len(json_data)} Mumbai Cardiologists pushed to MongoDB Atlas!")
else:
    print("⚠️ No matching doctors found to insert.")
