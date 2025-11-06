from unittest.mock import patch, MagicMock
from secrets_manager import SecretsManager, get_secrets_manager, get_secret


class TestSecretsManagerInitialization:
    def teardown_method(self):
        import secrets_manager

        secrets_manager._secrets_manager = None

    @patch("secrets_manager.os.getenv")
    def test_initialization_without_doppler_token(self, mock_getenv):
        def getenv_side_effect(key, default=""):
            if key == "DOPPLER_TOKEN":
                return ""
            if key == "DOPPLER_PROJECT":
                return "test-project"
            if key == "DOPPLER_CONFIG":
                return "dev"
            return default

        mock_getenv.side_effect = getenv_side_effect

        manager = SecretsManager()

        assert manager._doppler_initialized is False

    @patch("secrets_manager.os.getenv")
    def test_initialization_without_project_or_config(self, mock_getenv):
        def getenv_side_effect(key, default=""):
            if key == "DOPPLER_TOKEN":
                return "test_token"
            if key == "DOPPLER_PROJECT":
                return ""
            if key == "DOPPLER_CONFIG":
                return ""
            return default

        mock_getenv.side_effect = getenv_side_effect

        manager = SecretsManager()

        assert manager._doppler_initialized is False

    @patch("secrets_manager.os.getenv")
    @patch("secrets_manager.DopplerSDK")
    def test_initialization_with_doppler_exception(self, mock_sdk, mock_getenv):
        def getenv_side_effect(key, default=""):
            if key == "DOPPLER_TOKEN":
                return "test_token"
            if key == "DOPPLER_PROJECT":
                return "test-project"
            if key == "DOPPLER_CONFIG":
                return "dev"
            return default

        mock_getenv.side_effect = getenv_side_effect
        mock_sdk.side_effect = Exception("Connection failed")

        manager = SecretsManager()

        assert manager._doppler_initialized is False

    @patch("secrets_manager.os.getenv")
    @patch("secrets_manager.DopplerSDK")
    def test_initialization_with_empty_response(self, mock_sdk, mock_getenv):
        def getenv_side_effect(key, default=""):
            if key == "DOPPLER_TOKEN":
                return "test_token"
            if key == "DOPPLER_PROJECT":
                return "test-project"
            if key == "DOPPLER_CONFIG":
                return "dev"
            return default

        mock_getenv.side_effect = getenv_side_effect

        mock_client = MagicMock()
        mock_client.secrets.list.return_value = None
        mock_sdk.return_value = mock_client

        manager = SecretsManager()

        assert manager._doppler_initialized is False

    @patch("secrets_manager.os.getenv")
    @patch("secrets_manager.DopplerSDK")
    def test_initialization_with_falsy_response(self, mock_sdk, mock_getenv):
        def getenv_side_effect(key, default=""):
            if key == "DOPPLER_TOKEN":
                return "test_token"
            if key == "DOPPLER_PROJECT":
                return "test-project"
            if key == "DOPPLER_CONFIG":
                return "dev"
            return default

        mock_getenv.side_effect = getenv_side_effect

        mock_client = MagicMock()
        mock_client.secrets.list.return_value = 0
        mock_sdk.return_value = mock_client

        manager = SecretsManager()

        assert manager._doppler_initialized is False

    @patch("secrets_manager.os.getenv")
    @patch("secrets_manager.DopplerSDK")
    def test_successful_doppler_initialization(self, mock_sdk, mock_getenv):
        def getenv_side_effect(key, default=""):
            if key == "DOPPLER_TOKEN":
                return "test_token"
            if key == "DOPPLER_PROJECT":
                return "test-project"
            if key == "DOPPLER_CONFIG":
                return "dev"
            return default

        mock_getenv.side_effect = getenv_side_effect

        mock_response = MagicMock()
        mock_response.secrets = {"TEST_KEY": {"computed": "test_value"}}

        mock_client = MagicMock()
        mock_client.secrets.list.return_value = mock_response
        mock_sdk.return_value = mock_client

        manager = SecretsManager()

        assert manager._doppler_initialized is True


class TestSecretsManagerGetSecret:
    def teardown_method(self):
        import secrets_manager

        secrets_manager._secrets_manager = None

    @patch("secrets_manager.os.getenv")
    def test_get_secret_when_doppler_not_initialized(self, mock_getenv):
        def getenv_side_effect(key, default=""):
            return ""

        mock_getenv.side_effect = getenv_side_effect

        manager = SecretsManager()
        result = manager.get_secret("TEST_KEY")

        assert result is None

    @patch("secrets_manager.os.getenv")
    @patch("secrets_manager.DopplerSDK")
    def test_get_from_doppler_not_initialized(self, mock_sdk, mock_getenv):
        def getenv_side_effect(key, default=""):
            if key == "DOPPLER_TOKEN":
                return "test_token"
            if key == "DOPPLER_PROJECT":
                return "test-project"
            if key == "DOPPLER_CONFIG":
                return "dev"
            return default

        mock_getenv.side_effect = getenv_side_effect

        mock_response = MagicMock()
        mock_response.secrets = {}

        mock_client = MagicMock()
        mock_client.secrets.list.return_value = mock_response
        mock_sdk.return_value = mock_client

        manager = SecretsManager()
        manager._doppler_initialized = False

        result = manager._get_from_doppler("TEST_KEY")

        assert result is None

    @patch("secrets_manager.os.getenv")
    @patch("secrets_manager.DopplerSDK")
    def test_get_secret_successfully_from_doppler(self, mock_sdk, mock_getenv):
        def getenv_side_effect(key, default=""):
            if key == "DOPPLER_TOKEN":
                return "test_token"
            if key == "DOPPLER_PROJECT":
                return "test-project"
            if key == "DOPPLER_CONFIG":
                return "dev"
            return default

        mock_getenv.side_effect = getenv_side_effect

        mock_response = MagicMock()
        mock_response.secrets = {"TEST_KEY": {"computed": "test_value"}}

        mock_client = MagicMock()
        mock_client.secrets.list.return_value = mock_response
        mock_sdk.return_value = mock_client

        manager = SecretsManager()
        result = manager.get_secret("TEST_KEY")

        assert result == "test_value"

    @patch("secrets_manager.os.getenv")
    @patch("secrets_manager.DopplerSDK")
    def test_get_secret_with_caching(self, mock_sdk, mock_getenv):
        def getenv_side_effect(key, default=""):
            if key == "DOPPLER_TOKEN":
                return "test_token"
            if key == "DOPPLER_PROJECT":
                return "test-project"
            if key == "DOPPLER_CONFIG":
                return "dev"
            return default

        mock_getenv.side_effect = getenv_side_effect

        mock_response = MagicMock()
        mock_response.secrets = {"TEST_KEY": {"computed": "test_value"}}

        mock_client = MagicMock()
        mock_client.secrets.list.return_value = mock_response
        mock_sdk.return_value = mock_client

        manager = SecretsManager()

        result1 = manager.get_secret("TEST_KEY")
        assert result1 == "test_value"

        result2 = manager.get_secret("TEST_KEY")
        assert result2 == "test_value"

        assert mock_client.secrets.list.call_count == 1

    @patch("secrets_manager.os.getenv")
    @patch("secrets_manager.DopplerSDK")
    def test_get_secret_not_found_in_doppler(self, mock_sdk, mock_getenv):
        def getenv_side_effect(key, default=""):
            if key == "DOPPLER_TOKEN":
                return "test_token"
            if key == "DOPPLER_PROJECT":
                return "test-project"
            if key == "DOPPLER_CONFIG":
                return "dev"
            return default

        mock_getenv.side_effect = getenv_side_effect

        mock_response = MagicMock()
        mock_response.secrets = {"OTHER_KEY": {"computed": "other_value"}}

        mock_client = MagicMock()
        mock_client.secrets.list.return_value = mock_response
        mock_sdk.return_value = mock_client

        manager = SecretsManager()
        result = manager.get_secret("TEST_KEY")

        assert result is None

    @patch("secrets_manager.os.getenv")
    @patch("secrets_manager.DopplerSDK")
    def test_get_secret_with_exception(self, mock_sdk, mock_getenv):
        def getenv_side_effect(key, default=""):
            if key == "DOPPLER_TOKEN":
                return "test_token"
            if key == "DOPPLER_PROJECT":
                return "test-project"
            if key == "DOPPLER_CONFIG":
                return "dev"
            return default

        mock_getenv.side_effect = getenv_side_effect

        init_response = MagicMock()
        init_response.secrets = {}

        mock_client = MagicMock()
        mock_client.secrets.list.return_value = init_response
        mock_sdk.return_value = mock_client

        manager = SecretsManager()

        manager._secrets_cache.clear()

        result = manager.get_secret("TEST_KEY")

        assert result is None

    @patch("secrets_manager.os.getenv")
    @patch("secrets_manager.DopplerSDK")
    def test_get_from_doppler_with_exception_in_fetch(self, mock_sdk, mock_getenv):
        def getenv_side_effect(key, default=""):
            if key == "DOPPLER_TOKEN":
                return "test_token"
            if key == "DOPPLER_PROJECT":
                return "test-project"
            if key == "DOPPLER_CONFIG":
                return "dev"
            return default

        mock_getenv.side_effect = getenv_side_effect

        init_response = MagicMock()
        init_response.secrets = {"INITIAL_KEY": {"computed": "initial_value"}}

        mock_client = MagicMock()
        mock_client.secrets.list.return_value = init_response
        mock_sdk.return_value = mock_client

        manager = SecretsManager()

        manager._secrets_cache.clear()

        result = manager._get_from_doppler("TEST_KEY")

        assert result is None

    @patch("secrets_manager.os.getenv")
    @patch("secrets_manager.DopplerSDK")
    def test_get_from_doppler_with_cache_exception(self, mock_sdk, mock_getenv):
        def getenv_side_effect(key, default=""):
            if key == "DOPPLER_TOKEN":
                return "test_token"
            if key == "DOPPLER_PROJECT":
                return "test-project"
            if key == "DOPPLER_CONFIG":
                return "dev"
            return default

        mock_getenv.side_effect = getenv_side_effect

        init_response = MagicMock()
        init_response.secrets = {"INITIAL_KEY": {"computed": "initial_value"}}

        mock_client = MagicMock()
        mock_client.secrets.list.return_value = init_response
        mock_sdk.return_value = mock_client

        manager = SecretsManager()

        mock_cache = MagicMock()
        mock_cache.__contains__.side_effect = Exception("Unexpected cache error")
        manager._secrets_cache = mock_cache

        result = manager._get_from_doppler("TEST_KEY")

        assert result is None


class TestModuleLevelFunctions:
    def teardown_method(self):
        import secrets_manager

        secrets_manager._secrets_manager = None

    @patch("secrets_manager.os.getenv")
    def test_get_secrets_manager_singleton(self, mock_getenv):
        def getenv_side_effect(key, default=""):
            return ""

        mock_getenv.side_effect = getenv_side_effect

        manager1 = get_secrets_manager()
        manager2 = get_secrets_manager()

        assert manager1 is manager2

    @patch("secrets_manager.os.getenv")
    @patch("secrets_manager.DopplerSDK")
    def test_get_secret_module_function(self, mock_sdk, mock_getenv):
        def getenv_side_effect(key, default=""):
            if key == "DOPPLER_TOKEN":
                return "test_token"
            if key == "DOPPLER_PROJECT":
                return "test-project"
            if key == "DOPPLER_CONFIG":
                return "dev"
            return default

        mock_getenv.side_effect = getenv_side_effect

        mock_response = MagicMock()
        mock_response.secrets = {"TEST_KEY": {"computed": "test_value"}}

        mock_client = MagicMock()
        mock_client.secrets.list.return_value = mock_response
        mock_sdk.return_value = mock_client

        result = get_secret("TEST_KEY")

        assert result == "test_value"


class TestHelperFunctions:
    def teardown_method(self):
        import secrets_manager

        secrets_manager._secrets_manager = None

    @patch("secrets_manager.get_secret")
    def test_get_debug_mode_true_lowercase(self, mock_get_secret):
        mock_get_secret.return_value = "true"
        from secrets_manager import get_debug_mode

        result = get_debug_mode()
        assert result is True

    @patch("secrets_manager.get_secret")
    def test_get_debug_mode_true_uppercase(self, mock_get_secret):
        mock_get_secret.return_value = "TRUE"
        from secrets_manager import get_debug_mode

        result = get_debug_mode()
        assert result is True

    @patch("secrets_manager.get_secret")
    def test_get_debug_mode_one(self, mock_get_secret):
        mock_get_secret.return_value = "1"
        from secrets_manager import get_debug_mode

        result = get_debug_mode()
        assert result is True

    @patch("secrets_manager.get_secret")
    def test_get_debug_mode_yes(self, mock_get_secret):
        mock_get_secret.return_value = "yes"
        from secrets_manager import get_debug_mode

        result = get_debug_mode()
        assert result is True

    @patch("secrets_manager.get_secret")
    def test_get_debug_mode_false(self, mock_get_secret):
        mock_get_secret.return_value = "false"
        from secrets_manager import get_debug_mode

        result = get_debug_mode()
        assert result is False

    @patch("secrets_manager.get_secret")
    def test_get_debug_mode_none(self, mock_get_secret):
        mock_get_secret.return_value = None
        from secrets_manager import get_debug_mode

        result = get_debug_mode()
        assert result is False

    @patch("secrets_manager.get_secret")
    def test_get_debug_mode_random_string(self, mock_get_secret):
        mock_get_secret.return_value = "random"
        from secrets_manager import get_debug_mode

        result = get_debug_mode()
        assert result is False

    @patch("secrets_manager.get_secret")
    def test_get_log_level_with_value(self, mock_get_secret):
        mock_get_secret.return_value = "DEBUG"
        from secrets_manager import get_log_level

        result = get_log_level()
        assert result == "DEBUG"

    @patch("secrets_manager.get_secret")
    def test_get_log_level_none(self, mock_get_secret):
        mock_get_secret.return_value = None
        from secrets_manager import get_log_level

        result = get_log_level()
        assert result == "INFO"

    @patch("secrets_manager.get_secret")
    def test_get_log_level_empty_string(self, mock_get_secret):
        mock_get_secret.return_value = ""
        from secrets_manager import get_log_level

        result = get_log_level()
        assert result == "INFO"
