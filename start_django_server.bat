@echo off
cd /d C:\Users\pavan\kalyan\myapp\finalproject
start cmd /k "python manage.py runserver"
timeout /t 1 >nul
start http://127.0.0.1:8000
