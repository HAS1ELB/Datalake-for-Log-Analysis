FROM openjdk:8-jdk

# Variables d'environnement
ENV HADOOP_VERSION=3.3.4
ENV HIVE_VERSION=3.1.3
ENV HADOOP_HOME=/opt/hadoop
ENV HIVE_HOME=/opt/hive
ENV HADOOP_CONF_DIR=$HIVE_HOME/conf
ENV PATH=$PATH:$HADOOP_HOME/bin:$HADOOP_HOME/sbin:$HIVE_HOME/bin

# Installation des dépendances
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    curl \
    procps \
    net-tools \
    && rm -rf /var/lib/apt/lists/*

# Installation de Hadoop
RUN wget https://archive.apache.org/dist/hadoop/common/hadoop-${HADOOP_VERSION}/hadoop-${HADOOP_VERSION}.tar.gz \
    && tar -xzf hadoop-${HADOOP_VERSION}.tar.gz -C /opt/ \
    && rm hadoop-${HADOOP_VERSION}.tar.gz \
    && ln -s /opt/hadoop-${HADOOP_VERSION} ${HADOOP_HOME}

# Installation de Hive
RUN wget https://archive.apache.org/dist/hive/hive-${HIVE_VERSION}/apache-hive-${HIVE_VERSION}-bin.tar.gz \
    && tar -xzf apache-hive-${HIVE_VERSION}-bin.tar.gz -C /opt/ \
    && rm apache-hive-${HIVE_VERSION}-bin.tar.gz \
    && ln -s /opt/apache-hive-${HIVE_VERSION}-bin ${HIVE_HOME} \
    && mkdir -p ${HIVE_HOME}/data

# Copier les configurations Hadoop personnalisées pour Hive
COPY hadoop/configs/core-site.xml ${HADOOP_HOME}/etc/hadoop/
COPY hadoop/configs/hdfs-site.xml ${HADOOP_HOME}/etc/hadoop/
COPY hadoop/configs/mapred-site.xml ${HADOOP_HOME}/etc/hadoop/
COPY hadoop/configs/yarn-site.xml ${HADOOP_HOME}/etc/hadoop/

# Configuration de Hive
COPY hive/hive-site.xml ${HIVE_HOME}/conf/
RUN cp ${HADOOP_HOME}/etc/hadoop/core-site.xml ${HIVE_HOME}/conf/

WORKDIR ${HIVE_HOME}

# Exposer les ports pour HiveServer2, Hive Metastore
EXPOSE 10000 9083 10002


COPY scripts/run_beeline_with_retry.sh /scripts/
RUN chmod +x /scripts/run_beeline_with_retry.sh
RUN mkdir -p /opt/hive/logs

# Initialiser le schéma du metastore Derby
RUN $HIVE_HOME/bin/schematool -dbType derby -initSchema

# Démarrer HiveServer2
CMD ["hiveserver2"]