FROM python:3.9-slim

WORKDIR /app

# Installation des dépendances système
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    openjdk-11-jdk \
    curl \
    wget \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Installation des bibliothèques Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Variables d'environnement pour Java et Hadoop
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
ENV HADOOP_HOME=/opt/hadoop
ENV PATH=$PATH:$HADOOP_HOME/bin:$HADOOP_HOME/sbin

# Téléchargement des clients Hadoop et Hive
RUN wget https://downloads.apache.org/hadoop/common/hadoop-3.2.1/hadoop-3.2.1.tar.gz && \
    tar -xzf hadoop-3.2.1.tar.gz && \
    mv hadoop-3.2.1 /opt/hadoop && \
    rm hadoop-3.2.1.tar.gz

RUN wget https://downloads.apache.org/hive/hive-3.1.2/apache-hive-3.1.2-bin.tar.gz && \
    tar -xzf apache-hive-3.1.2-bin.tar.gz && \
    mv apache-hive-3.1.2-bin /opt/hive && \
    rm apache-hive-3.1.2-bin.tar.gz

ENV HIVE_HOME=/opt/hive
ENV PATH=$PATH:$HIVE_HOME/bin

COPY . .

CMD ["tail", "-f", "/dev/null"]