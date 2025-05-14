FROM openjdk:8-jdk

# Variables d'environnement
ENV HADOOP_VERSION=3.3.4
ENV SQOOP_VERSION=1.4.7
ENV HADOOP_HOME=/opt/hadoop
ENV SQOOP_HOME=/opt/sqoop
ENV PATH=$PATH:$HADOOP_HOME/bin:$HADOOP_HOME/sbin:$SQOOP_HOME/bin
ENV HADOOP_CLASSPATH=/opt/sqoop/gen-classes/*
ENV CLASSPATH=$CLASSPATH:${SQOOP_HOME}/lib

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

# Copier les configurations Hadoop personnalisées
COPY hadoop/configs/core-site.xml ${HADOOP_HOME}/etc/hadoop/
COPY hadoop/configs/hdfs-site.xml ${HADOOP_HOME}/etc/hadoop/
COPY hadoop/configs/mapred-site.xml ${HADOOP_HOME}/etc/hadoop/
COPY hadoop/configs/yarn-site.xml ${HADOOP_HOME}/etc/hadoop/

# Installation de Sqoop
RUN wget https://archive.apache.org/dist/sqoop/${SQOOP_VERSION}/sqoop-${SQOOP_VERSION}.bin__hadoop-2.6.0.tar.gz \
    && tar -xzf sqoop-${SQOOP_VERSION}.bin__hadoop-2.6.0.tar.gz -C /opt/ \
    && rm sqoop-${SQOOP_VERSION}.bin__hadoop-2.6.0.tar.gz \
    && ln -s /opt/sqoop-${SQOOP_VERSION}.bin__hadoop-2.6.0 ${SQOOP_HOME}

# Ajout du driver MySQL pour Sqoop
RUN wget https://repo1.maven.org/maven2/mysql/mysql-connector-java/8.0.28/mysql-connector-java-8.0.28.jar \
    && mv mysql-connector-java-8.0.28.jar ${SQOOP_HOME}/lib/

# Ajout de commons-lang3 pour Sqoop
RUN wget https://repo1.maven.org/maven2/org/apache/commons/commons-lang3/3.12.0/commons-lang3-3.12.0.jar \
    && mv commons-lang3-3.12.0.jar ${SQOOP_HOME}/lib/

# Ajout de commons-lang (older version) pour Sqoop
RUN wget https://repo1.maven.org/maven2/commons-lang/commons-lang/2.6/commons-lang-2.6.jar \
    && mv commons-lang-2.6.jar ${SQOOP_HOME}/lib/

# Create libjars directory for Sqoop
RUN mkdir -p ${SQOOP_HOME}/libjars

# Configuration de Sqoop
RUN cp ${HADOOP_HOME}/etc/hadoop/core-site.xml ${SQOOP_HOME}/conf/
RUN cp ${HADOOP_HOME}/etc/hadoop/hdfs-site.xml ${SQOOP_HOME}/conf/

# Script d'entrée
COPY sqoop/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

WORKDIR ${SQOOP_HOME}

ENTRYPOINT ["/entrypoint.sh"]
