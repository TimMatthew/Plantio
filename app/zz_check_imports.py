from __future__ import annotations

try:
    import beanie  # noqa: F401
except Exception:
    beanie = None  # type: ignore[assignment]

try:
    import fastapi  # noqa: F401
except Exception:
    fastapi = None  # type: ignore[assignment]


def info() -> str:
    import sys

    fv = getattr(fastapi, "__version__", "unknown") if fastapi else "unknown"
    bv = getattr(beanie, "__version__", "unknown") if beanie else "unknown"
    return f"{sys.executable}\nfastapi {fv} | beanie {bv}"


if __name__ == "__main__":
    print(info())
