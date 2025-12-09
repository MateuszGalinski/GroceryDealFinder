Run redis on wsl
command for celery: celery -A core worker -l info -P solo
command for beat: celery -A core beat -l info