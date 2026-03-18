"""
runner.py - シンプルなテストランナー

pytest を使わずにテストを実行するための共通ユーティリティ。
各テストファイルから import して使用する。

使い方:
    from runner import TestRunner

    runner = TestRunner("テスト名")
    runner.run(test_func, page)
    sys.exit(runner.summary())
"""

import sys
import traceback


class TestRunner:
    """シンプルなテストランナー"""

    def __init__(self, name: str = ""):
        self.name = name
        self.passed = 0
        self.failed = 0
        self.skipped = 0
        self.errors: list[tuple[str, Exception]] = []

    def run(self, test_func, *args, skip_reason: str | None = None, **kwargs):
        """テスト関数を実行する

        Args:
            test_func: 実行するテスト関数
            *args: テスト関数に渡す引数（page, context, browser 等）
            skip_reason: スキップ理由（指定するとテストをスキップ）
        """
        name = test_func.__name__
        if skip_reason:
            self.skipped += 1
            print(f"  ⏭ {name} (SKIP: {skip_reason})")
            return
        try:
            test_func(*args, **kwargs)
            self.passed += 1
            print(f"  ✓ {name}")
        except AssertionError as e:
            self.failed += 1
            self.errors.append((name, e))
            print(f"  ✗ {name}")
            traceback.print_exc()
        except Exception as e:
            self.failed += 1
            self.errors.append((name, e))
            print(f"  ✗ {name}: {type(e).__name__}")
            traceback.print_exc()

    def summary(self) -> int:
        """結果サマリーを表示し、終了コードを返す

        Returns:
            0: 全テスト成功、1: 失敗あり
        """
        total = self.passed + self.failed + self.skipped
        print(f"\n{'='*60}")
        title = f" {self.name}" if self.name else ""
        print(
            f"Results{title}: "
            f"{self.passed} passed, {self.failed} failed, "
            f"{self.skipped} skipped / {total} total"
        )
        if self.errors:
            print(f"\nFailed tests:")
            for name, err in self.errors:
                print(f"  - {name}: {err}")
        print(f"{'='*60}")
        return 0 if self.failed == 0 else 1
