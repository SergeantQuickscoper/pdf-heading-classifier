FROM openjdk:17-slim

RUN apt-get update && \
    apt-get install -y maven python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . /app

RUN pip3 install --no-cache-dir -r model/requirements.txt

RUN mvn dependency:go-offline
RUN mvn dependency:resolve-plugins
RUN mvn package -DskipTests
RUN mvn exec:java

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"] 