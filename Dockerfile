FROM python:3.11-slim
EXPOSE 5000
WORKDIR /app



# Install pip requirements
COPY requirements.txt /app/
# Copy the uploads folder to the container
COPY uploads /app/uploads
COPY models /app/models

RUN python -m pip install -r requirements.txt
COPY . /app

# Install system dependencies and Tesseract
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-eng \
    tesseract-ocr-osd \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Verify Tesseract installation and data files
RUN tesseract --version && \
    ls -l /usr/share/tesseract-ocr/4.00/tessdata/eng.traineddata || ls -l /usr/share/tesseract-ocr/*/tessdata/eng.traineddata

# Set Tesseract environment variables
ENV TESSDATA_PREFIX=/usr/share/tesseract-ocr/4.00/tessdata/
ENV PATH="/usr/share/tesseract-ocr/4.00/tessdata/:${PATH}"



# Install OpenCV dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1


# Install textract using pip3
RUN pip3 install --no-cache-dir textract
RUN pip install pytesseract
RUN pip install redis

# Test Tesseract installation
RUN python -c "import pytesseract; print(pytesseract.get_tesseract_version())"

# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
CMD ["python","app.py"]