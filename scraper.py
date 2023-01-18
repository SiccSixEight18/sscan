import requests
from bs4 import BeautifulSoup
import csv

def scrape(url, element):
  # Make a request to the website and retrieve the HTML
  r = requests.get(url)
  html = r.text
  
  # Use BeautifulSoup to parse the HTML
  soup = BeautifulSoup(html, 'html.parser')
  
  # Find all instances of the element on the page
  target_elements = soup.find_all(element)
  
  # Open a CSV file for writing
  with open('scraped_elements.csv', 'w', newline='') as csvfile:
    # Create a CSV writer
    writer = csv.writer(csvfile)
    
    # Write the element text to the CSV file
    for element in target_elements:
      writer.writerow([element.text])

# Test the function
url = 'https://www.ss.com/lv/transport/cars/bmw/316/'
element = '<td>'
scrape(url, element)
