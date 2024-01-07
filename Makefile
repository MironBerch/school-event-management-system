.PHONY: lint
lint:
	flake8
	isort -qc .

.PHONY: fix
fix:
	isort .

.PHONY: compile-requirements
compile-requirements:
	pip show -q pip-tools || pip install pip-tools
	cd requirements/ && pip-compile requirements.in
	cd requirements/ && pip-compile requirements.lint.in

.PHONY: sync-requirements
sync-requirements:
	pip show -q pip-tools || pip install pip-tools
	cd requirements/ && pip-sync requirements.txt requirements.*.txt
