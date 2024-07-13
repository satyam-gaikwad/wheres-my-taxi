from calendar import c
import requests 
import numpy as np
import requests
from bs4 import BeautifulSoup


url = "https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page"  # Replace with your URL
output_file = "/home/user/Desktop/wheres-my-taxi/wheres-my-taxi/parquet_files.txt"  # Replace with your desired output file path

response = requests.get(url)

# Parse the HTML content using BeautifulSoup
soup = BeautifulSoup(response.content, 'html.parser')
count = 0
for a in soup.find_all('a', href=True):
    href = a['href']
    if 'yellow_tripdata' in href:
        if href not in output_file.split("\n"):
            count += 1
            with open(output_file, "a") as file:  # Use "a" mode to append to the file instead of overwriting it
                file.write(href + "\n")
            print("Parquet file name has been saved:", href)

if count != 0:
    with open("/home/user/Desktop/wheres-my-taxi/wheres-my-taxi/results.txt", "w") as file:
        file.write("1\n" + str(count))



 
#this file works best toetract all file links for yellow taxi data from the nyc.gov website



