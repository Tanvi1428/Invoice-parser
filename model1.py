from PIL import Image
import pytesseract
from . import extract


def parse(image_path):
    # image_path="D:\\invoice\\backend\\uploads\\pic1.png"
    img = Image.open(image_path)
    text = pytesseract.image_to_string(img,config='--psm 4')
    json = extract.extract(text)
    print(json)
    return json


