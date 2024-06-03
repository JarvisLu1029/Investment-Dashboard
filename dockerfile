FROM python:3.11
LABEL maintainer="Jarvis"
RUN apt update
RUN apt upgrade -y
RUN apt-get install -y tmux
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
# command1 || command2 第一個指令執行有錯誤 就會執行第二個
RUN dpkg -i google-chrome-stable_current_amd64.deb || apt-get install -f -y
RUN dpkg -i google-chrome-stable_current_amd64.deb
RUN pip install --upgrade pip
COPY requirements.txt ./
# 自行建立更新清單 不要使用快取目錄(會下載最新版本的套件)
RUN pip install --no-cache-dir -r requirements.txt