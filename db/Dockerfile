FROM pgvector/pgvector:pg15

# Install pgvector extension package from PGDG
RUN apt-get update \
 && apt-get install -y --no-install-recommends postgresql-15-pgvector \
 && rm -rf /var/lib/apt/lists/*

# The base image entrypoint will run any scripts in /docker-entrypoint-initdb.d/

