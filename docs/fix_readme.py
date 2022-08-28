import os

with open('../README.md', 'r') as file:
    content = file.read()
content = content.replace(
    '_images/', 'https://raw.githubusercontent.com/UN-GCPDS/python-gcpds.visualizations/main/docs/source/notebooks/_images/')
with open('../README.md', 'w') as file:
    file.write(content)
