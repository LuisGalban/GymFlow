import os
import unittest
from unittest.mock import patch, MagicMock


class TestH01_JWTSecretNoDefault(unittest.TestCase):
    """H-01: JWT_SECRET must not have a default value."""

    def test_jwt_secret_missing_raises_value_error(self):
        env = {k: v for k, v in os.environ.items() if k != "JWT_SECRET"}
        with patch.dict(os.environ, env, clear=True):
            with patch("dotenv.load_dotenv", return_value=None):
                import sys
                mod_name = "app.auth.auth"
                saved = sys.modules.pop(mod_name, None)
                try:
                    with self.assertRaises(ValueError):
                        __import__(mod_name)
                finally:
                    if saved is not None:
                        sys.modules[mod_name] = saved

    def test_jwt_secret_no_hardcoded_default(self):
        import inspect
        import app.auth.auth as auth_mod
        source = inspect.getsource(auth_mod)
        self.assertNotIn(
            "super_secret_key_default",
            source,
            "auth.py must not contain a hardcoded JWT_SECRET default",
        )

    def test_jwt_secret_value_error_message(self):
        env = {k: v for k, v in os.environ.items() if k != "JWT_SECRET"}
        with patch.dict(os.environ, env, clear=True):
            with patch("dotenv.load_dotenv", return_value=None):
                import sys
                mod_name = "app.auth.auth"
                saved = sys.modules.pop(mod_name, None)
                try:
                    with self.assertRaises(ValueError) as ctx:
                        __import__(mod_name)
                    self.assertIn("JWT_SECRET", str(ctx.exception))
                finally:
                    if saved is not None:
                        sys.modules[mod_name] = saved


if __name__ == "__main__":
    unittest.main()
