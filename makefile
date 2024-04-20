data:
	mkdir -p data
	python -B src/get_data.py
analyze:
	mkdir -p figs
	python -B src/analysis.py
clean:
	rm -rf data
	rm -rf figs
