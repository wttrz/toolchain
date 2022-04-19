clean:
	source env/bin/activate && pip3 uninstall serene && pip3 freeze > requirements.txt
