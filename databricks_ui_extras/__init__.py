try:
    from importlib.metadata import version, PackageNotFoundError
except ImportError:  # Python < 3.10 (backport)
    from importlib_metadata import version, PackageNotFoundError

try:
    __version__ = version("databricks-secrets-explorer")
except PackageNotFoundError:
    # package is not installed
    pass