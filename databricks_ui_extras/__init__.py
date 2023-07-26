try:
    from importlib.metadata import version, PackageNotFoundError
except ImportError:  # Python < 3.10 (backport)
    from importlib_metadata import version, PackageNotFoundError

try:
    __version__ = version("databricks-ui-extras")
except PackageNotFoundError:
    # package is not installed
    pass

from databricks_ui_extras.app import Page
from databricks_ui_extras.app import RootPage


def wire_dbutils_for_ws_client(mod):
    from databricks.sdk import WorkspaceClient
    from databricks_ui_extras import app
    dbutils = globals()["dbutils"]
    mod.ws_client = WorkspaceClient(
        host=dbutils.notebook.entry_point.getDbutils().notebook().getContext().apiUrl().getOrElse(None),
        token=dbutils.notebook.entry_point.getDbutils().notebook().getContext().apiToken().getOrElse(None)
    )
