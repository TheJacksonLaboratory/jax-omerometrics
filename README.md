# jax-omerometrics
Repo for generating OMERO reports/dashboards

Create an environment. Currently working dependency versions are in `requirements.txt`.
```
python -m venv <venv_path>
source <venv_path>/bin/activate
pip install https://github.com/glencoesoftware/zeroc-ice-py-linux-x86_64/releases/download/20240202/zeroc_ice-3.6.5-cp39-cp39-manylinux_2_28_x86_64.whl
pip install ezomero pandas requests
```

Copy `config_example.py` to `config.py` and fill in values.

Collect data with `python collect_daily.py FOLDER` or `python collect_hourly.py FOLDER`.
