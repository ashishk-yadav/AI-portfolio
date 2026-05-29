FROM python:3.11-slim
WORKDIR /app
# app.py uses huggingface_hub InferenceClient (API call) — no local weights needed
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "app.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--server.headless=true"]
