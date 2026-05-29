FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# Pre-download VGG-19 weights
RUN python -c "import torchvision.models as m; m.vgg19(weights='IMAGENET1K_V1')"
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "streamlit_app.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--server.headless=true", \
     "--server.baseUrlPath=/app/12"]
