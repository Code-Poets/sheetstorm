# sheetstorm
Base application for management of employees working hours

## Software requirements
- Python 3.7.0
- Django 2.1.1
- Django REST framework 3.8.2

## Environment set-up

Clone following repository:
```
git clone https://github.com/Code-Poets/sheetstorm.git
```

**NOTE:** Upon completing all steps for required OS, please refer to the [local configuration](#local-configuration) sub-section.

### Ubuntu
    
1. Install Python 3.7.0 by running in terminal
    ```
    sudo apt install python3.7
    ```
    You can verify the installation by running: `python3.7 --version`

2. Install PIP:
    ```
    sudo apt install python3-pip
    ```
    You can verify the installation by running: `python3.7 -m pip`.

3. Install virtualenv with PIP: 
    ```
    sudo python3.7 -m pip install virtualenv
    ```

4. Create new virtualenv and install all dependencies:
    ```
    virtualenv ~/.virtualenvs/sheetstorm --python python3.7
    . ~/.virtualenvs/sheetstorm/bin/activate
    pip install pip --upgrade
    
    # Dependencies for running sheetstorm application
    pip install --requirement sheetstorm/requirements.lock
    ```

5. Install PostgreSQL:
    ```
    sudo apt install postgresql postgresql-contrib
    ```

6. With administrative rights, edit file located in */etc/postgresql/<version>/main/pg_hba.conf*. Change ***\<method\>*** to ***trust*** in the following line:
    ```
    local   all             postgres                                <method>
    ```
    Restart PostgreSQL:
    ```
    sudo service postgresql restart
    ```

7. Create database for application: 
    ```
    createdb -U postgres sheetstorm
    ```



### Mac OS

1. Install Xcode command-line tools by running `xcode-select --install` in terminal.

2. Install Homebrew:
    ```
    ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
    ```

3. Install Python 3.7.0: 
    ```
    brew install python
    ```
    You can verify the installation by running `python3 --version`.

4. Install PIP: 
    ```
    sudo easy_install pip
    ```
    You can verify the installation by running: `pip3 --version`.

5. Install virtualenv with PIP:
    ```
    pip3 install virtualenv
    ```

6. Create new virtualenv and install all dependencies:
    ```
    virtualenv ~/.virtualenvs/sheetstorm --python python3.7
    source ~/.virtualenvs/sheetstorm/bin/activate
    pip install pip --upgrade

    # Dependencies for running sheetstorm application
    pip install --requirement sheetstorm/requirements.lock
    ```

7. Install PostgreSQL with `brew install postgresql`.
    
    Create a database cluster: 
    ```
    initdb /usr/local/var/postgres
    ```

8.  With administrative rights, edit file located in */usr/local/var/postgres/pg_hba.conf*. Change ***\<method\>*** to ***trust*** in the following line:
    ```
    local   all             postgres                                <method>
    ```
    Restart PostgreSQL:
    ```
    brew services restart postgresql
    ```
    If server is unavailable, even though homebrew claims that service is running, try manual restart with:
    ```
    pg_ctl -D /usr/local/var/postgres restart
    ```

9. Create database for application: 
    ```
    createdb -U postgres sheetstorm
    ```



### Windows

1. Install Python 3.7.0 with [web-based installer](https://www.python.org/ftp/python/3.7.0/python-3.7.0-amd64-webinstall.exe).
    
    You can verify Python installation by running `python --version` in Command Prompt.
    
    You can verify PIP installation by running `pip --version`.

2. Install virtualenv with PIP: 
    ```
    pip3 install virtualenv
    ```
    
3. Create new virtualenv and install all dependencies:
    ```
    virtualenv ~/.virtualenvs/sheetstorm --python python3.7
    <your venv location>\Scripts\activate
    pip install pip --upgrade

    # Dependencies for running sheetstorm application
    pip install --requirement sheetstorm/requirements.lock
    ```

4. Install BigSQL PGC and PostgreSQL 10.5: 
    ```
    cd C:\
    
    #Install BigSQL PGC
    @powershell -NoProfile -ExecutionPolicy unrestricted -Command "iex ((new-object net.webclient).DownloadString('https://s3.amazonaws.com/pgcentral/install.ps1'))"
    
    #Install PostgreSQL
    cd bigsql
    pgc install pg10
    ```

5.  Edit file located in *C:\bigsql\pg10\init\pg_hba.conf*, add the following line to file:
    ```
    local   all             postgres                                trust
    ```   
    Restart PostgreSQL:
    ```
    C:\bigsql\pgc restart pg10
    ```

6. Create database for application by running the following command in Command Prompt: 
    ```
    C:\bigsql\pg10\bin\createdb -U postgres sheetstorm.
    ```



### Local configuration

Create your local configuration in */sheetstorm/settings/local_settings.py*
```
from .development import *
```
If your database configuration differs from the defaults, you may need to tweak the values below and add them to your local_settings.py too:
```
DATABASES['default']['NAME'] = 'sheetstorm'
DATABASES['default']['USER'] = 'postgres'
DATABASES['deafult']['PASSWORD'] = ''
```
