# INSTRUCTIONS
- We need to install SQL database
```console
sudo apt install postgresql postgresql-contrib
```
- Enter SQL with postgres user
```console
sudo -u postgres psql
```
- Creating database table
```console
CREATE DATABASE project_db;
```
- Creating user and password
```console
CREATE USER project_app WITH PASSWORD 'test';
```
- Granting privileges for user
```console
GRANT ALL PRIVILEGES ON DATABASE project_db TO project_app;
```
- Upgrade database
```console
flask db upgrade
```

**NOTE:** IF YOU STILL GET PRIVILEGE ERROR, USE THE FOLLOWING COMMAND BELOW;
```console
sudo -u postgres psql -d project_db -c "GRANT ALL ON SCHEMA public TO project_app;"
```

