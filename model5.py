
import textract
from . import extract

image_path="uploads\\pic1.png"
def parse(img_path):

    # Extract text from an image
    text = textract.process(img_path)
    #print(text.decode())
    json = extract.extract(text)
    return json