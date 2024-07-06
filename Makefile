quality_checks:
	isort .
	black .
	pylint --recursive=y .
