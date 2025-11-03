import os
import logging
from typing import Any

from dopplersdk import DopplerSDK
from dotenv import load_dotenv

logger = logging.getLogger("daily_learner")

load_dotenv()


class SecretsManager:
    def __init__(self):
        self._doppler_initialized: bool = False
        self._secrets_cache: dict[str, Any] = {}
        self._doppler_client: DopplerSDK | None = None
        self.doppler_token: str = os.getenv("DOPPLER_TOKEN", "")
        self.doppler_project: str = os.getenv("DOPPLER_PROJECT", "")
        self.doppler_config: str = os.getenv("DOPPLER_CONFIG", "")
        self._initialize_doppler()

    def _initialize_doppler(self) -> None:
        if not self.doppler_token:
            logger.warning("DOPPLER_TOKEN not set.")
            return

        if not self.doppler_project or not self.doppler_config:
            logger.warning("DOPPLER_PROJECT or DOPPLER_CONFIG not set.")
            return

        try:
            self._doppler_client = DopplerSDK()
            self._doppler_client.set_access_token(self.doppler_token)

            secrets_list = self._doppler_client.secrets.list(
                project=self.doppler_project,
                config=self.doppler_config,
            )

            if not secrets_list:
                raise Exception(
                    "Failed to initialize Doppler client cannot fetch secrets or secret_list is empty"
                )

            for key, value in secrets_list.secrets.items():
                self._secrets_cache[key] = value.get("computed")

            self._doppler_initialized = True

        except Exception as e:
            logger.warning(f"Failed to initialize Doppler client: {e}.")
            self._doppler_initialized = False
            self._doppler_client = None

    def _get_from_doppler(self, key: str) -> str | None:
        if not self._doppler_initialized:
            return None

        try:
            if key in self._secrets_cache:
                return self._secrets_cache[key]

        except Exception as e:
            logger.error(f"Error retrieving secret '{key}' from Doppler: {e}")
            return None

    def get_secret(self, key: str) -> str | None:
        if not self._doppler_initialized:
            logger.warning(f"Doppler not initialized, cannot retrieve secret '{key}'")
            return None

        value = self._get_from_doppler(key)
        if value is not None:
            return value
        logger.warning(f"Secret '{key}' not found in Doppler")
        return None


_secrets_manager: SecretsManager | None = None


def get_secrets_manager() -> SecretsManager:
    global _secrets_manager
    if _secrets_manager is None:
        _secrets_manager = SecretsManager()
    return _secrets_manager


def get_secret(key: str) -> str | None:
    return get_secrets_manager().get_secret(key)


def get_debug_mode() -> bool:
    debug_value = get_secret("DEBUG_MODE")
    if debug_value is None:
        return False
    return debug_value.lower() in ("true", "1", "yes")


def get_log_level() -> str:
    log_level = get_secret("LOG_LEVEL")
    return log_level if log_level else "INFO"
