from paddleocr import PaddleOCR
from . import extract

def Paddleocr(image_path):
    ocr = PaddleOCR(use_angle_cls=True, lang='en')
    # image_path = "D:\\invoice\\backend\\uploads\\pic1.png"

    # Run OCR on the image
    result = ocr.ocr(image_path)

    # Extract text (correctly handle the nested structure)
    text = ' '.join(word_info[1][0] for line in result for word_info in line)
    json = extract.extract(text)
    #return {"text": text}


