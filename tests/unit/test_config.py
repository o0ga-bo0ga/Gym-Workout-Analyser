from src.config import env_bool


class TestEnvBool:
    def test_default_false(self, monkeypatch):
        monkeypatch.delenv("TEST_VAR", raising=False)
        assert env_bool("TEST_VAR") is False

    def test_default_true(self, monkeypatch):
        monkeypatch.delenv("TEST_VAR", raising=False)
        assert env_bool("TEST_VAR", True) is True

    def test_string_true(self, monkeypatch):
        monkeypatch.setenv("TEST_VAR", "true")
        assert env_bool("TEST_VAR") is True

    def test_string_false(self, monkeypatch):
        monkeypatch.setenv("TEST_VAR", "false")
        assert env_bool("TEST_VAR") is False

    def test_string_yes(self, monkeypatch):
        monkeypatch.setenv("TEST_VAR", "yes")
        assert env_bool("TEST_VAR") is True

    def test_string_1(self, monkeypatch):
        monkeypatch.setenv("TEST_VAR", "1")
        assert env_bool("TEST_VAR") is True

    def test_string_0_default_false(self, monkeypatch):
        monkeypatch.setenv("TEST_VAR", "0")
        assert env_bool("TEST_VAR", False) is False

    def test_string_0_default_true(self, monkeypatch):
        monkeypatch.setenv("TEST_VAR", "0")
        assert env_bool("TEST_VAR", True) is False


class TestConfigDefaults:
    def test_lyfta_enabled_default(self, monkeypatch):
        monkeypatch.delenv("LYFTA_ENABLED", raising=False)
        from importlib import reload

        import src.config
        reload(src.config)
        assert src.config.LYFTA_ENABLED is True

    def test_database_enabled_default(self, monkeypatch):
        monkeypatch.delenv("DATABASE_ENABLED", raising=False)
        from importlib import reload

        import src.config
        reload(src.config)
        assert src.config.DATABASE_ENABLED is True

    def test_gemini_mode_default(self, monkeypatch):
        monkeypatch.delenv("GEMINI_MODE", raising=False)
        from importlib import reload

        import src.config
        reload(src.config)
        assert src.config.GEMINI_MODE is True
