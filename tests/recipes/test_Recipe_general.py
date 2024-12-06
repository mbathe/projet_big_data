import pytest
from unittest.mock import patch
import locale
import logging

def test_locale_setting():
    with patch('locale.setlocale') as mock_setlocale:
        # Simulate the first call raising an exception, second call succeeds
        mock_setlocale.side_effect = [locale.Error("Locale not found"), None]

        # Re-import the module to execute the code block
        import sys
        module_name = 'src.pages.recipes.Analyse_recipes'
        if module_name in sys.modules:
            del sys.modules[module_name]
        # Now import the module, which should execute the locale setting code
        import src.pages.recipes.Analyse_recipes

        # Verify that locale.setlocale was called twice
        assert mock_setlocale.call_count == 2
        # Verify the calls with correct arguments
        mock_setlocale.assert_any_call(locale.LC_TIME, 'fr_FR.UTF-8')
        mock_setlocale.assert_any_call(locale.LC_TIME, '')


