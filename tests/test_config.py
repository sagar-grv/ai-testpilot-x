def test_config_loads():
    import config
    assert hasattr(config, "settings")

def test_settings_fields():
    import config
    s = config.settings
    assert hasattr(s, "GEMINI_API_KEY")
    assert hasattr(s, "DB_URL")
    assert hasattr(s, "CHROMA_PATH")
    assert hasattr(s, "EXECUTION_MODE")

def test_execution_mode_valid():
    import config
    assert config.settings.EXECUTION_MODE in ("LOCAL", "MOCK", "GRID")

def test_db_url_sqlite():
    import config
    assert "sqlite" in config.settings.DB_URL.lower()
