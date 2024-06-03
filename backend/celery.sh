#!/bin/bash

# 建立一個新的 tmux 會話，名稱為 'celery'
tmux new-session -d -s celery

# 在 'celery' 中建立第一個窗口並執行任務
tmux send-keys -t celery:0 'celery -A dashboard worker --loglevel=info -f logs/celery.log' C-m

# 建立第二個窗口
tmux new-window -t celery

# 在第二個窗口執行另一個任務
tmux send-keys -t celery:1 'celery -A dashboard beat --loglevel=info -f logs/celery.log' C-m

# echo "Waiting SQL....."
# sleep 10

# echo "Start Django server"
# python manage.py runserver 0.0.0.0:80

# 防止容器退出
tail -f /dev/null