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

# 2. Scrape the REAL Website (Wikipedia - Nobel Prize in Medicine)
real_url = "https://en.wikipedia.org/wiki/List_of_Nobel_laureates_in_Physiology_or_Medicine"
print(f"🌐 Navigating to {real_url}..." )
driver.get(real_url)
time.sleep(3)

# Grab the text, but limit to 5000 characters so we don't overload the LLM
raw_text = driver.find_element(By.TAG_NAME, "body").text[:5000]
driver.quit()
print("✅ Real Data Scraped!")

# 3. Process with LLM
client = Groq(api_key=os.environ["GROQ_API_KEY"])
prompt = f"""
Extract the Nobel laureates in Medicine mentioned in this text. 
Format as a strict JSON array with keys: 'year', 'name', 'rationale'.
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
collection = db["providers"]

# Notice: I removed the delete_many() line! Now your database will grow!
collection.insert_many(json_data)
print(f"✅ SUCCESS! {len(json_data)} real records pushed to MongoDB Atlas!")
