grep -r src/ -E -e "TODO|FIXME" > TODO
source ./env/bin/activate && pip3 freeze > requirements.txt
