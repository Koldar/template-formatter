# Intoduction #

This project allows you to gnerate a file from a jinja2 template file

# Create executable #

To create an executable of this project, enter in the assocaited virtual env (venv) and perform the following (require pyinstaller to be installed):

```
cd pycharm/
pip install pyinstaller
pyinstaller --onefile --nowindow --icon="icon\jinja.ico" --name="template-formatter" template_formatter\main.py

```

# Create dist with setuptools

```
cd pycharm/
source venv/bin/activate
pip install semver
python setup.py build sdist 
```

# Install on your system

```
cd pycharm/
source venv/bin/activate
pip install semver
python setup.py install
```