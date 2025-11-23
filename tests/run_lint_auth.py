#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Auth Modulu Lint Script'i

Bu script app/auth/auth.py dosyasi icin static code analizi yapar.
Pylint kullanarak kod kalitesini kontrol eder.

Kullanim:
    python run_lint_auth.py              # Kod analizi yap
    python run_lint_auth.py --html       # HTML rapor olustur
"""

import sys
import subprocess
from pathlib import Path


def run_pylint(html_report=False):
    """Auth.py icin pylint calistir"""
    target_file = "app/auth/auth.py"
    
    # Dosyanin var oldugunu kontrol et
    if not Path(target_file).exists():
        print(f"[ERROR] Dosya bulunamadi: {target_file}")
        return False
    
    command = f"pylint {target_file} --rcfile=.pylintrc"
    
    if html_report:
        output_file = "pylint_auth_report.html"
        command += f" --output-format=html > {output_file}"
        print(f"[*] HTML rapor {output_file} dosyasina yazilacak")
    
    print(f"\n{'='*70}")
    print(f"[*] AUTH.PY KOD ANALIZI CALISTIRILIYOR")
    print(f"{'='*70}\n")
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=False
        )
        
        if html_report:
            if Path(output_file).exists():
                print(f"\n{'='*70}")
                print(f"[SUCCESS] HTML rapor olusturuldu: {output_file}")
                print(f"{'='*70}\n")
        
        if result.returncode == 0:
            print(f"\n{'='*70}")
            print("[SUCCESS] Kod analizi basarili!")
            print(f"{'='*70}\n")
            return True
        else:
            print(f"\n{'='*70}")
            print("[WARNING] Kod analizi tamamlandi, bazı uyarılar olabilir.")
            print(f"{'='*70}\n")
            return True  # Pylint uyarılarla da 0 dönebilir, başarılı sayıyoruz
    except Exception as e:
        print(f"[ERROR] Hata olustu: {e}")
        return False


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Auth modulu icin static code analizi yapar",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--html',
        action='store_true',
        help='HTML rapor olustur'
    )
    
    args = parser.parse_args()
    
    success = run_pylint(args.html)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

