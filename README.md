# **Prerequisites :**

Minimum Python 3.3 installation to be able to create the virtual environment.

# **Virtual environment installation :**

Go to the directory where you want to install the virtual environment. 
Execute the command:
`python3 -m venv 'env'` 
*('env' will be the directory where the python environment data will be stored)*

# **Activation and installation of the dependencies necessary for the script in the virtual environment :**

## Under Windows the commands to be executed :

`env/Script/activate`,
`pip install -r requirements.txt`

## Under Linux the commands to be executed :

`source env/bin/activate`,
`pip install -r requirements.txt`

## Installation dependencies manually :

`pip install beautifulsoup4~= 4.9.1 requests~= 2.25.1 csv~= 1.0`

## Execution of application code :

`python3 main.py`
