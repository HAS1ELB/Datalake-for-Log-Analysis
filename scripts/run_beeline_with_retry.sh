#!/bin/bash

MAX_ATTEMPTS=5
ATTEMPT_NUM=1
HIVE_SCRIPT_FILE="/scripts/create_hive_tables.hql"
HIVE_JDBC_URL="jdbc:hive2://localhost:10000"

echo "Attempting to connect to HiveServer2 at ${HIVE_JDBC_URL} and run ${HIVE_SCRIPT_FILE}..."

until beeline -u "${HIVE_JDBC_URL}" -e "show databases;" &> /dev/null
do
    if [ ${ATTEMPT_NUM} -eq ${MAX_ATTEMPTS} ]; then
        echo "Failed to connect to HiveServer2 after ${MAX_ATTEMPTS} attempts. Exiting."
        exit 1
    fi
    echo "Attempt ${ATTEMPT_NUM} failed. Retrying in 7 seconds..."
    ATTEMPT_NUM=$((ATTEMPT_NUM+1))
    sleep 7
done

echo "Successfully connected to HiveServer2."
echo "Running Hive script: ${HIVE_SCRIPT_FILE}"

beeline -u "${HIVE_JDBC_URL}" -f "${HIVE_SCRIPT_FILE}"

exit $?