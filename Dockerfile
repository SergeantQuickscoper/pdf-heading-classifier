FROM openjdk:17-slim

RUN apt-get update && \
    apt-get install -y python3 python3-pip maven && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . /app

WORKDIR /app/extractor

RUN mvn dependency:go-offline
RUN mvn dependency:resolve-plugins
RUN mvn package -DskipTests
RUN mvn exec:java

WORKDIR /app/semanticAnalyzer

RUN pip3 install --no-cache-dir numpy && \
    pip3 install --no-cache-dir torch==2.2.0+cpu \
    --extra-index-url https://download.pytorch.org/whl/cpu && \
    pip3 install --no-cache-dir -r requirements.txt


RUN chmod +x /app/semanticAnalyzer/entrypoint.sh

ENTRYPOINT ["/app/semanticAnalyzer/entrypoint.sh"] 
