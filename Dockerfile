FROM python:3.9-slim

# Install system dependencies (Java, APKTool requirements, apksigner, zipalign)
RUN apt-get update && \
    apt-get install -y default-jdk wget zip unzip apksigner zipalign && \
    rm -rf /var/lib/apt/lists/*

# Setup APKTool
ENV APKTOOL_VERSION=2.9.3
RUN wget https://github.com/iBotPeaches/Apktool/releases/download/v${APKTOOL_VERSION}/apktool_${APKTOOL_VERSION}.jar -O /usr/local/bin/apktool.jar
COPY apktool.sh /usr/local/bin/apktool
RUN chmod +x /usr/local/bin/apktool /usr/local/bin/apktool.jar

# Generate a default debug keystore for signing
RUN keytool -genkey -v -keystore /root/debug.keystore \
    -storepass android -alias androiddebugkey -keypass android \
    -keyalg RSA -keysize 2048 -validity 10000 \
    -dname "CN=Android Debug,O=Android,C=US"

# Set working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create temp directories for processing
RUN mkdir -p /app/temp /app/uploads /app/outputs

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
