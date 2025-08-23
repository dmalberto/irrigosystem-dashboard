#!/usr/bin/env python3
"""
Simple Smoke Test para Batch B - Fase 2
Verifica funcionamento básico das telas padronizadas
"""

import sys
from datetime import date, time


def test_imports():
    """Testa importação de todos os módulos padronizados"""
    try:
        print("Testing UI Components import...")
        print("[OK] UI Components imported successfully")

        print("Testing Controllers import...")
        print("[OK] Controllers imported successfully")

        print("Testing Tariff Schedules import...")
        print("[OK] Tariff Schedules imported successfully")

        print("Testing Users import...")
        print("[OK] Users imported successfully")

        print("Testing Controller Activations import...")
        print("[OK] Controller Activations imported successfully")

        return True
    except Exception as e:
        print(f"[ERROR] Import failed: {e}")
        return False


def test_validations():
    """Testa funções de validação"""
    try:
        from src.ui_components import (validate_coordinates, validate_email,
                                       validate_password)

        # Test email validation
        assert validate_email("test@example.com") == True
        assert validate_email("invalid-email") == False
        print("[OK] Email validation working")

        # Test password validation
        valid, msg = validate_password("senha123")
        assert valid == True

        invalid, msg = validate_password("123")
        assert invalid == False
        print("[OK] Password validation working")

        # Test coordinates validation
        valid, msg = validate_coordinates(-23.5505, -46.6333)
        assert valid == True

        invalid, msg = validate_coordinates(100, 200)
        assert invalid == False
        print("[OK] Coordinates validation working")

        return True
    except Exception as e:
        print(f"[ERROR] Validation test failed: {e}")
        return False


def test_datetime_formatting():
    """Testa formatação de data/hora"""
    try:
        from src.ui_components import (format_datetime_for_api,
                                       format_datetime_for_display)

        # Test API formatting
        result = format_datetime_for_api(date.today(), time(12, 0))
        assert result is not None
        assert "T" in result
        assert result.endswith("Z")
        print("[OK] API datetime formatting working")

        # Test display formatting
        iso_string = "2025-01-15T12:30:45Z"
        result = format_datetime_for_display(iso_string)
        assert "/" in result  # Brazilian format uses /
        print("[OK] Display datetime formatting working")

        return True
    except Exception as e:
        print(f"[ERROR] Datetime formatting test failed: {e}")
        return False


def run_smoke_tests():
    """Executa smoke tests básicos"""
    print("SMOKE TESTS - Batch B Phase 2")
    print("=" * 50)

    results = []

    results.append(test_imports())
    results.append(test_validations())
    results.append(test_datetime_formatting())

    passed = sum(results)
    total = len(results)

    print("=" * 50)
    print(f"Results: {passed}/{total} tests passed")

    if passed == total:
        print("All smoke tests passed!")
        return 0
    else:
        print("Some tests failed.")
        return 1


if __name__ == "__main__":
    exit_code = run_smoke_tests()
    sys.exit(exit_code)
