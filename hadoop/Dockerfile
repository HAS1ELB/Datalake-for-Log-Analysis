FROM openjdk:8-jdk

# Variables d'environnement
ENV HADOOP_VERSION=3.3.4
ENV HADOOP_HOME=/opt/hadoop
ENV PATH=$PATH:$HADOOP_HOME/bin:$HADOOP_HOME/sbin

# Installation des dépendances
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    curl \
    gnupg \
    procps \
    net-tools \
    && rm -rf /var/lib/apt/lists/*

# Téléchargement et installation de Hadoop
RUN wget https://archive.apache.org/dist/hadoop/common/hadoop-${HADOOP_VERSION}/hadoop-${HADOOP_VERSION}.tar.gz \
    && tar -xzf hadoop-${HADOOP_VERSION}.tar.gz -C /opt/ \
    && rm hadoop-${HADOOP_VERSION}.tar.gz \
    && ln -s /opt/hadoop-${HADOOP_VERSION} ${HADOOP_HOME} \
    && mkdir -p ${HADOOP_HOME}/logs

# Configuration de Hadoop
COPY configs/core-site.xml ${HADOOP_HOME}/etc/hadoop/
COPY configs/hdfs-site.xml ${HADOOP_HOME}/etc/hadoop/
COPY configs/mapred-site.xml ${HADOOP_HOME}/etc/hadoop/
COPY configs/yarn-site.xml ${HADOOP_HOME}/etc/hadoop/

RUN mkdir -p /hadoop/dfs/name /hadoop/dfs/data

WORKDIR $HADOOP_HOME

# Exposer les ports nécessaires
EXPOSE 9870 9864 9000 8020

CMD ["hdfs"]
