from google.cloud import secretmanager


class SecretsClient:
    def __init__(self):
        self._client = secretmanager.SecretManagerServiceAsyncClient()

    async def get(self, secret):
        resp = await self._client.access_secret_version(
            name=f"projects/trebek/secrets/{secret}/versions/latest"
        )
        return resp.payload.data.decode()
