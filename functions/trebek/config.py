import yaml

import aiofiles


class ConfigClient:
    def __init__(self, config_file="config.yaml"):
        self._config_file = config_file

    async def __aenter__(self):
        async with aiofiles.open(self._config_file, "r") as f:
            contents = await f.read()
            return yaml.load(contents, Loader=yaml.SafeLoader)

    async def __aexit__(self, exc_type, exc, backtrace):
        pass
