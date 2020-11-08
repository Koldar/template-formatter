# Intoduction #

This project allows you to gnerate a file from a jinja2 template file

# Create executable #

To create an executable of this project, enter in the assocaited virtual env (venv) and perform the following:

```
cd pycharm/
pyinstaller --onefile --nowindow --icon="icon\jinja.ico" --name="template-formatter" template_formatter\main.py

```