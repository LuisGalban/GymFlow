import inspect
import os
import re
import unittest


class TestH04_CookieSecureFlag(unittest.TestCase):
    """H-04: Cookie secure flag must be read from environment variable COOKIE_SECURE."""

    def _get_cookie_block(self):
        import app.main as main_mod
        source = inspect.getsource(main_mod)
        lines = source.split("\n")
        cookie_block_lines = []
        capture = False
        for line in lines:
            if 'key="gymflow_token"' in line:
                capture = True
            if capture:
                cookie_block_lines.append(line)
                if "secure=" in line.lower():
                    break
        return "\n".join(cookie_block_lines)

    def test_no_hardcoded_secure_false_in_source(self):
        cookie_block = self._get_cookie_block()
        self.assertNotIn(
            "secure=False",
            cookie_block,
            "Cookie secure flag must NOT be hardcoded to False in source code",
        )

    def test_no_hardcoded_secure_true_in_source(self):
        cookie_block = self._get_cookie_block()
        self.assertNotIn(
            "secure=True",
            cookie_block,
            "Cookie secure flag must NOT be hardcoded to True in source code",
        )

    def test_cookie_secure_reads_env_variable(self):
        import app.main as main_mod
        source = inspect.getsource(main_mod)
        self.assertIn(
            "COOKIE_SECURE",
            source,
            "Cookie secure flag must read from COOKIE_SECURE environment variable",
        )

    def test_cookie_secure_env_conversion_pattern(self):
        import app.main as main_mod
        source = inspect.getsource(main_mod)
        pattern = re.compile(r'os\.\w+(?:\.\w+)*\(["\']COOKIE_SECURE["\']')
        self.assertTrue(
            pattern.search(source),
            "COOKIE_SECURE must be read via os.environ or os.getenv",
        )


if __name__ == "__main__":
    unittest.main()
