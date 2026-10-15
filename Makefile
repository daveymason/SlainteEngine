.PHONY: all run up down stop restart status test logs ingest help

all: run

run:
	@./run.sh start

up:
	@./run.sh start

down:
	@./run.sh stop

stop:
	@./run.sh stop

restart:
	@./run.sh restart

status:
	@./run.sh status

test:
	@./run.sh test

logs:
	@./run.sh logs

ingest:
	@./run.sh ingest

help:
	@./run.sh help
