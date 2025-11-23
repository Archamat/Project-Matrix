#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Auth Modulu Test Script'i

Bu script app/auth/auth.py modulu için unit testleri calistirir.
Sadece auth.py ile ilgili testleri calistirir.

Kullanim:
    python run_tests_auth.py              # Testleri calistir
    python run_tests_auth.py --coverage   # Coverage raporu ile
"""

import sys
import subprocess


def run_pytest(coverage=False, verbose=True):
    """Auth testlerini calistir"""
    command = "pytest tests/test_auth.py"
    
    if verbose:
        command += " -v"
    
    if coverage:
        command += " --cov=app.auth.auth --cov-report=html --cov-report=term"
    
    print(f"\n{'='*70}")
    print(f"[*] AUTH MODULU TESTLERI CALISTIRILIYOR")
    print(f"{'='*70}\n")
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=False
        )
        
        if result.returncode == 0:
            print(f"\n{'='*70}")
            print("[SUCCESS] Tum testler basarili!")
            print(f"{'='*70}\n")
            return True
        else:
            print(f"\n{'='*70}")
            print("[FAILED] Bazı testler basarisiz!")
            print(f"{'='*70}\n")
            return False
    except Exception as e:
        print(f"[ERROR] Hata olustu: {e}")
        return False


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Auth modulu icin unit testleri calistirir",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--coverage',
        action='store_true',
        help='Code coverage raporu olustur'
    )
    
    parser.add_argument(
        '--quiet',
        action='store_true',
        help='Sessiz mod (verbose kapali)'
    )
    
    args = parser.parse_args()
    
    success = run_pytest(args.coverage, not args.quiet)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

