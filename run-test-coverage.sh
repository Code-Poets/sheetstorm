#!/usr/bin/env bash
pytest 					        \
	--cov-report term-missing 	\
	--cov-config coverage-config \
	--cov=.
rm .coverage