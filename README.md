# 🚀 Apache Airflow 2.7.3 Setup Guide on RHEL

This guide provides step-by-step instructions for installing **Apache Airflow 2.7.3** with **PostgreSQL** as the metadata database on **RHEL**.

## 📌 Prerequisites

Ensure you have Python 3.8+, PostgreSQL 12+, `pip`, and `virtualenv` installed.

## 🛠️ Installation

Remove any existing virtual environment:

```sh
mkdir airflow & cd airflow
rm -rf venv
```

Create and activate a new virtual environment:

```sh
python3 -m venv venv
source venv/bin/activate
```

Install Apache Airflow with PostgreSQL support:

```sh
pip install "apache-airflow[postgres]==2.7.3" --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.7.3/constraints-$(python -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")').txt"
```

## 🗄️ Configure PostgreSQL

Install PostgreSQL:

```sh
sudo yum install -y postgresql-server postgresql-contrib
```

Initialize and start PostgreSQL:

```sh
sudo postgresql-setup initdb
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

Create an Airflow database and user:

```sh
sudo -u postgres psql
```

Run:

```sql
CREATE DATABASE airflow;
CREATE USER airflow WITH PASSWORD 'airflow';
ALTER ROLE airflow SET client_encoding TO 'utf8';
ALTER ROLE airflow SET default_transaction_isolation TO 'read committed';
ALTER ROLE airflow SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE airflow TO airflow;
\q
```

## ⚙️ Configure Airflow

Edit the `airflow.cfg` file:

```sh
nano ~/airflow/airflow.cfg
```

Update:

```ini
sql_alchemy_conn = postgresql+psycopg2://airflow:airflow@localhost/airflow
```

Initialize the database:

```sh
airflow db init
```

Migrate exiting database: (optional)

```sh
airflow db migrate
```

## 🔐 Create an Admin User

```sh
airflow users create --username admin --password admin --firstname Admin --lastname User --role Admin --email admin@example.com
```

## 🚀 Start Airflow Services

Start the webserver:

```sh
airflow webserver --port 8080
```

Start the scheduler:

```sh
airflow scheduler
```

## 🌐 Access Airflow UI

Visit **[http://localhost:8080](http://localhost:8080)**  
Login with **admin / admin**

## ✅ Verification

Check dependencies:

```sh
pip list | grep -E "flask|werkzeug|pyjwt"
```

Test database connection:

```sh
airflow db check
```

Check Airflow installation:

```sh
airflow info
```
