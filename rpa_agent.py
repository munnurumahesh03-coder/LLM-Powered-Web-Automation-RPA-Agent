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

# 2. Scrape the REAL Website (Wikipedia - Indian Cardiologists)
real_url = "https://en.wikipedia.org/wiki/Category:Indian_cardiologists"
print(f"🌐 Navigating to {real_url}..." )
driver.get(real_url)
time.sleep(3)

# Grab the text, limiting to 5000 characters to fit the LLM context window
raw_text = driver.find_element(By.TAG_NAME, "body").text[:5000]
driver.quit()
print("✅ Real Data Scraped!")

# 3. Process with LLM (Extracting Real Indian Cardiologists)
client = Groq(api_key=os.environ["GROQ_API_KEY"])
prompt = f"""
Extract the doctors mentioned in this text. 
Format as a strict JSON array with keys: 'name', 'specialty', 'location'.
CRITICAL RULE: Set the 'specialty' to 'Cardiology' and 'location' to 'India' for all of them.
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
print("✅ Data Cleaned by AI!")

# 4. Push to MongoDB
mongo_client = MongoClient(os.environ["MONGO_URI"])
db = mongo_client["hextgen_medtech"]

# Put them in a clean, professional folder
collection = db["indian_cardiologists"] 

collection.delete_many({}) # Clears old data so you only have the fresh, real list
if len(json_data) > 0:
    collection.insert_many(json_data)
    print(f"✅ SUCCESS! {len(json_data)} real Indian cardiologists pushed to MongoDB Atlas!")
else:
    print("⚠️ No matching doctors found to insert.")
