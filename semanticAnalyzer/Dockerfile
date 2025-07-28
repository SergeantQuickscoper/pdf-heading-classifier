FROM openjdk:17-slim

RUN apt-get update && \
    apt-get install -y python3 python3-pip maven && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY .. /app

RUN pip3 install --no-cache-dir -r model/requirements.txt

WORKDIR /app/extractor
RUN mvn compile

WORKDIR /app/semanticAnalyzer

ENTRYPOINT ["/entrypoint.sh"] 
