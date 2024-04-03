#!/bin/sh

/venv/bin/python -m alembic upgrade head 
/venv/bin/python -m app
