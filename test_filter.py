import requests

url = "http://localhost:8000/process"
files = {"raw_file": open("recent.csv", "w")} # Mock CSV for the test
open("recent.csv", "w").write("Username,Full Name,Batch,Raw Score\nF1,John,6C1,10\nF2,Jane,7C1,20\n")

data = {"batches": "7C1"}

try:
    response = requests.post(url, files={"raw_file": open("recent.csv", "rb")}, data=data)
    print("Response JSON:")
    print(response.json())
except Exception as e:
    print("Error:", e)
