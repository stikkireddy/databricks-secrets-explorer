try:
    from importlib.metadata import version, PackageNotFoundError
except ImportError:  # Python < 3.10 (backport)
    from importlib_metadata import version, PackageNotFoundError

try:
    __version__ = version("databricks-ui-extras")
except PackageNotFoundError:
    # package is not installed
    pass