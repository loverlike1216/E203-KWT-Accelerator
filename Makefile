PYTHON ?= envs/model/bin/python
LAYERS ?= 1
CONFIG ?= v1/config/official.template.json
.PHONY: env-check model-check dataset-check quant-check sim-reference-soc sim-engine sim-soc synth-reference equiv-reference regress synth sta power benchmark package
env-check model-check dataset-check quant-check sim-reference-soc sim-engine sim-soc synth-reference equiv-reference regress synth sta power benchmark package:
	$(PYTHON) v1/scripts/run.py $@ --layers $(LAYERS) --config $(CONFIG)
