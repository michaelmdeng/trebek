import yaml


class TrebekConfig:
    def __init__(self):
        with open("config.yaml", "r") as f:
            self._config = yaml.load(f, Loader=yaml.SafeLoader)

    @property
    def config(self):
        return self._config
