import requests
from . import extract
api_key = "K88940105388957"  # You need to get an API key from OCR.space
image_path = "uploads\\pic1.png"

def parse(img_path):
    # Upload the image to OCR.space
    with open(img_path, 'rb') as image_file:
        files = {'file': image_file}
        data = {'apikey': api_key}
        response = requests.post('https://api.ocr.space/parse/image', files=files, data=data)

    # Get the text from the response
    result = response.json()
    text = result['ParsedResults'][0]['ParsedText']
    #print(text)
    json = extract.extract(text)
    return json
