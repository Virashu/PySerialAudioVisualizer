# Visualizer

> Make sound into cool visual effects in real time!

> [!IMPORTANT]  
> Needs loopback audio source

## Usage

```shell
poetry install
poetry shell
python -m vaudio <args>
```

or

```shell
python -m venv .venv
source .venv/bin/activate

python -m pip install -r requirements.txt

python -m pip install .
python -m vaudio <args>
```

## Options

### --mode

Visualizer supports two modes: `fft` and `rolling`

## Arduino firmware

[virashu/viravis_arduino](https://github.com/virashu/viravis_arduino)
