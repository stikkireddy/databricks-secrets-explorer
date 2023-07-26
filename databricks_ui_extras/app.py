import os
from pathlib import Path
from typing import Callable, List, Tuple, cast, Optional

import reacton.ipyvuetify as v
import solara
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.workspace import ScopeBackendType
from solara.lab.toestand import Reactive

import databricks_ui_extras

ws_client = WorkspaceClient(profile=os.environ.get("DATABRICKS_CONFIG_PROFILE", None))


def get_all_secrets(scope_name):
    return [[secret.key, secret.last_updated_timestamp] for secret in ws_client.secrets.list_secrets(scope_name)]


def get_all_secret_scopes():
    return ws_client.secrets.list_scopes()


# global state
selected_scope = solara.reactive("")
scopes = solara.reactive(get_all_secret_scopes())
selected_secrets: Reactive[List[Tuple[str, int]]] = solara.reactive([])
delete_prompt_asset_type = solara.reactive("")
delete_prompt_asset_name = solara.reactive("")
delete_prompt_asset_id = solara.reactive("")


def reset_delete_prompt():
    delete_prompt_asset_type.value = ""
    delete_prompt_asset_name.value = ""
    delete_prompt_asset_id.value = ""


@solara.component
def CreateScopeForm(show_dialog: Callable[[bool], None]):
    valid_backends = ["DATABRICKS"]
    backend = solara.use_reactive("DATABRICKS")
    scope = solara.use_reactive("")
    error_msg = solara.use_reactive("")

    def on_create_scope():
        print(f"create scope attempt: {backend.value} {scope.value}")
        if scope.value is None or scope.value == "":
            error_msg.value = "Scope name cannot be empty"
            return
        if scope.value in [secret.name for secret in scopes.value]:
            error_msg.value = "Scope already exists"
            return
        try:
            print(f"create scope in progress: {backend.value} {scope.value}")
            backend_scope = [be for be in ScopeBackendType if be.value == backend.value][0]
            ws_client.secrets.create_scope(scope=scope.value, scope_backend_type=backend_scope)
        except Exception as e:
            print(f"create scope failed: {backend.value} {scope.value}")
            error_msg.value = str(e)
            return
        print(f"create scope success: {backend.value} {scope.value}")
        scopes.value = get_all_secret_scopes()
        selected_scope.value = scope.value
        selected_secrets.value = get_all_secrets(scope.value)
        show_dialog(False)

    with solara.Card("Create Secret Scope", style="max-width: 584px"):
        with solara.Column():
            if error_msg.value is not None and error_msg.value != "":
                solara.Error(error_msg.value)
            solara.InputText(label="Scope Name", value=scope)
            solara.Select(label="Backend", value=backend, values=valid_backends)
            with solara.Row():
                solara.Button("Create", on_click=on_create_scope)
                solara.Button("Cancel", on_click=lambda: show_dialog(False))


@solara.component
def EditScopeForm(scope: Reactive[str], secret_key: Reactive[str], show_dialog: Callable[[bool], None]):
    secret_value = solara.use_reactive("")
    error_msg = solara.use_reactive("")

    def on_edit_secret():
        print(f"save secret: {scope.value} {secret_key.value} {secret_value.value}")
        if secret_value.value is None or secret_value.value == "":
            error_msg.value = "Secret value cannot be empty"
            return
        try:
            ws_client.secrets.put_secret(scope=scope.value, key=secret_key.value, string_value=secret_value.value)
            print(scope.value, secret_key.value, secret_value.value)
            print(f"save secret success: {scope.value} {secret_key.value}")
        except Exception as e:
            print(f"save secret failed: {scope.value} {secret_key.value}")
            error_msg.value = str(e).replace(secret_key.value, "********")
            return

        show_dialog(False)

    with solara.Card("Edit Secret", style="max-width: 584px"):
        with solara.Column():
            if error_msg.value is not None and error_msg.value != "":
                solara.Error(error_msg.value)
            solara.InputText(label="Scope Name", value=scope, disabled=True)
            solara.InputText(label="Secret Name", value=secret_key, disabled=True)
            solara.InputText(label="Secret Value", value=secret_value, password=True)
            # v.TextField(v_model=text, on_v_model=set_text, label="Scope Name")
            with solara.Row():
                solara.Button("Save", on_click=on_edit_secret)
                solara.Button("Cancel", on_click=lambda: show_dialog(False))


@solara.component
def CreateSecretForm(scope: Reactive[str], show_dialog: Callable[[bool], None]):
    secret_key = solara.use_reactive("")
    secret_value = solara.use_reactive("")
    error_msg = solara.use_reactive("")

    def on_create_secret():
        print(f"create secret attempt: {scope.value} {secret_key.value}")
        if secret_key.value is None or secret_key.value == "":
            error_msg.value = "Key name cannot be empty"
            return
        if secret_key.value in [secret[0] for secret in selected_secrets.value]:
            error_msg.value = "Key already exists"
            return
        if secret_value.value is None or secret_value.value == "":
            error_msg.value = "Secret value cannot be empty"
            return
        try:
            ws_client.secrets.put_secret(scope=scope.value, key=secret_key.value, string_value=secret_value.value)
            # ws_client.secrets.create_scope(scope=scope.value, scope_backend_type=backend_scope)
        except Exception as e:
            print(f"create scope failed: {scope.value} {secret_key.value}")
            error_msg.value = str(e).replace(secret_key.value, "********")
            return
        print(f"create scope success: {scope.value} {secret_key.value}")
        selected_secrets.value = get_all_secrets(scope.value)
        show_dialog(False)

    with solara.Card("Create Secret", style="max-width: 584px"):
        with solara.Column():
            if error_msg.value is not None and error_msg.value != "":
                solara.Error(error_msg.value)
            solara.InputText(label="Scope Name", value=scope, disabled=True)
            solara.InputText(label="Secret Name", value=secret_key, )
            solara.InputText(label="Secret Value", value=secret_value, password=True)
            with solara.Row():
                solara.Button("Save", on_click=on_create_secret)
                solara.Button("Cancel", on_click=lambda: show_dialog(False))


@solara.component
def PromptDelete(callback, show_dialog: Callable[[bool], None], title=None, warning_msg=None):
    error_msg = solara.use_reactive("")

    def on_delete():
        if delete_prompt_asset_id.value is None or delete_prompt_asset_id.value == "":
            print("Delete failed: ", delete_prompt_asset_type.value, delete_prompt_asset_name.value)
            error_msg.value = "Asset ID cannot be empty"
            return
        callback()
        show_dialog(False)

    def on_cancel():
        show_dialog(False)

    with v.Dialog(v_model=True, persistent=True, max_width="600px"):
        with solara.Card(title or f"Delete {delete_prompt_asset_type.value} "
                                  f"{delete_prompt_asset_name.value}", style="max-width: 584px"):
            with solara.Column():
                if error_msg.value is not None and error_msg.value != "":
                    solara.Error(error_msg.value)
                solara.Markdown(warning_msg or f"Are you sure you want to delete this "
                                               f"{delete_prompt_asset_type.value} with name: "
                                               f"{delete_prompt_asset_name.value}?")
                with solara.Row():
                    solara.Button("Delete", on_click=on_delete)
                    solara.Button("Cancel", on_click=on_cancel)


@solara.component
def SecretsBrowser():
    selected_secret_key = solara.use_reactive("")
    create_scope = solara.use_reactive(False)
    edit_secret = solara.use_reactive(False)
    create_secret = solara.use_reactive(False)
    show_delete_secret_prompt = solara.use_reactive(False)
    show_delete_scope_prompt = solara.use_reactive(False)

    def on_change(val):
        selected_secrets.value = get_all_secrets(val)

    def set_create_scope(val):
        create_scope.value = val

    def set_create_secret(val):
        create_secret.value = val

    def set_edit_secret(val):
        edit_secret.value = val

    def set_show_delete_secret_prompt(val):
        show_delete_secret_prompt.value = val

    def set_show_delete_scope_prompt(val):
        show_delete_scope_prompt.value = val

    with v.Dialog(v_model=create_secret.value, persistent=True, max_width="600px",
                  on_v_model=set_create_secret):
        if create_secret.value is True:  # 'reset' the component state on open/close
            CreateSecretForm(selected_scope, set_create_secret)

    # create_secret_dialog(create_scope)
    with v.Dialog(v_model=edit_secret.value, persistent=True, max_width="600px",
                  on_v_model=set_edit_secret):
        if edit_secret.value is True:  # 'reset' the component state on open/close
            EditScopeForm(selected_scope, selected_secret_key, set_edit_secret)

    with v.Dialog(v_model=create_scope.value, persistent=True, max_width="600px",
                  on_v_model=set_create_scope):
        if create_scope.value is True:  # 'reset' the component state on open/close
            CreateScopeForm(set_create_scope)

    with solara.Card("Browse Scopes", style="min-width: 500px"):
        with solara.Row(style="align-items: center;"):
            solara.Select(label="Scopes", value=selected_scope, values=[scope.name for scope in scopes.value],
                          on_value=on_change)
            solara.Button("Create Scope", on_click=lambda: set_create_scope(True))
            if selected_scope.value is not None and selected_scope.value != "":

                def on_delete_scope():
                    delete_prompt_asset_type.value = "secret scope"
                    delete_prompt_asset_name.value = selected_scope.value
                    delete_prompt_asset_id.value = selected_scope.value
                    set_show_delete_scope_prompt(True)

                def on_delete_scope_callback():
                    print("Delete attempt: ", selected_scope.value)
                    try:
                        ws_client.secrets.delete_scope(scope=selected_scope.value)
                        print("Delete success: ", selected_scope.value, )
                        # reset the state of all scopes and selected secrets
                        scopes.value = get_all_secret_scopes()
                        selected_secrets.value = []
                        selected_scope.value = ""
                    except Exception as e:
                        print("Delete failed: ", selected_scope.value)
                        print(e)
                    reset_delete_prompt()

                with v.Dialog(v_model=show_delete_scope_prompt.value, persistent=True, max_width="600px",
                              on_v_model=set_show_delete_scope_prompt):
                    if show_delete_scope_prompt.value is True:
                        PromptDelete(
                            title=f"Delete Secret Scope: {selected_scope.value}",
                            warning_msg="Are you sure you want to delete this secret scope?",
                            callback=on_delete_scope_callback,
                            show_dialog=set_show_delete_scope_prompt
                        )
                solara.Button(f"Delete Scope: {selected_scope.value}", on_click=on_delete_scope)

        if selected_scope.value is not None and selected_scope.value != "":
            with solara.Column():
                solara.Button("Create Secret", on_click=lambda: set_create_secret(True))
                for secret in selected_secrets.value:
                    def on_edit_secret(this_key=secret):
                        print("selected for edit", this_key[0])
                        selected_secret_key.value = this_key[0]
                        set_edit_secret(True)

                    def on_delete_secret(this_key=secret):
                        delete_prompt_asset_type.value = "secret"
                        delete_prompt_asset_name.value = this_key[0]
                        delete_prompt_asset_id.value = this_key[0]
                        set_show_delete_secret_prompt(True)

                    def on_delete_callback():
                        try:
                            print("Delete attempt: ", delete_prompt_asset_type.value, delete_prompt_asset_name.value)
                            ws_client.secrets.delete_secret(scope=selected_scope.value,
                                                            key=delete_prompt_asset_id.value)
                            print("Delete success: ", delete_prompt_asset_type.value, delete_prompt_asset_name.value)
                            reset_delete_prompt()
                            selected_secrets.value = get_all_secrets(selected_scope.value)
                        except Exception as e:
                            print("Delete failed: ", delete_prompt_asset_type.value, delete_prompt_asset_name.value)
                            print(e)

                    with v.Dialog(v_model=show_delete_secret_prompt.value, persistent=True, max_width="600px",
                                  on_v_model=set_show_delete_secret_prompt):
                        if show_delete_secret_prompt.value is True:
                            PromptDelete(
                                title=f"Delete Secret: {delete_prompt_asset_name.value} "
                                      f"from Scope: {selected_scope.value}",
                                warning_msg="Are you sure you want to delete this secret?",
                                callback=on_delete_callback,
                                show_dialog=set_show_delete_secret_prompt
                            )

                    with solara.Row(style="align-items: center;"):
                        solara.Markdown(f"##### **Secret Key:** {secret[0]}", style="padding: inherit;")
                        solara.Markdown(f"##### **Updated Timestamp:** {secret[1]}", style="padding: inherit;")
                        solara.Button(icon_name="mdi-pencil", icon=True, on_click=on_edit_secret)
                        solara.Button(icon_name="mdi-delete", icon=True, on_click=on_delete_secret)


# Path("/Users/sri.tikkireddy/PycharmProjects/databricks-secrets-explorer").resolve()
# Path("/Users/sri.tikkireddy/PycharmProjects/databricks-secrets-explorer").resolve()


@solara.component
def FileBrowser(exec_base_path, exclude_prefixes: List[str] = None):
    file, set_file = solara.use_state(cast(Optional[Path], None))
    path, set_path = solara.use_state(cast(Optional[Path], None))
    # directory, set_directory = solara.use_state(EXECUTION_BASE_PATH)
    EXECUTION_BASE_PATH = Path(exec_base_path).resolve()
    directory = solara.use_reactive(EXECUTION_BASE_PATH)
    message = solara.use_reactive(None)
    MAX_FILE_CT = 10000
    exclude_prefixes = exclude_prefixes or []

    with solara.Column():
        # can_select = solara.ui_checkbox("Enable select")

        # def reset_path():
        #     set_path(None)
        #     set_file(None)

        def filter_path(p: Path) -> bool:
            if any([str(p).startswith(prefix) for prefix in exclude_prefixes]):
                return False
            return True
            # return p.is_dir()

        # reset path and file when can_select changes
        # solara.use_memo(reset_path)

        # def on_directory_change(p: Path) -> None:
        #     set_directory(p)
        def protect():
            def check_base_path(value):
                if not str(value).startswith(str(EXECUTION_BASE_PATH)):
                    directory.value = EXECUTION_BASE_PATH
                    message.value = f"Cannot leave root base path {EXECUTION_BASE_PATH}!"
                else:
                    message.value = None

            return directory.subscribe(check_base_path)

        solara.use_effect(protect)
        if message.value:
            error = message.value
        elif path is None:
            error = "You must select a project root!"
        else:
            error = None

        def count_dir():
            count = 0
            for root, dirs, files in os.walk(str(path), topdown=False):
                for _ in files:
                    count += 1
                    if count > MAX_FILE_CT:
                        return count
            return count

        def download_dir():
            if path is not None and path.is_dir():
                import io
                import zipfile
                zip_buffer = io.BytesIO()
                zf = zipfile.ZipFile(zip_buffer, mode='w')

                def remove_prefix(text, prefix):
                    if text.startswith(prefix):
                        return text[len(prefix):]
                    return text

                for root, dirs, files in os.walk(str(path), topdown=False):
                    for name in files:
                        # zf.writestr()
                        this_file = str(os.path.join(root, name))
                        in_zip_name = remove_prefix(this_file, str(path) + "/")
                        with open(this_file, "rb") as f:
                            zf.writestr(in_zip_name, f.read())
                zf.close()
                return zip_buffer

        def on_path_select(p: Path) -> None:
            if str(p).startswith(str(EXECUTION_BASE_PATH)):
                set_path(p)
                message.value = None

        if path is not None and path.is_file():
            solara.Info(f"You selected file for download: {path}")
            # must be lambda otherwise will always try to download
            solara.FileDownload(lambda: path.open("rb"), path.name, label=f"Download {path.name} From DBFS")

        if path is not None and path.is_dir():
            file_ct = count_dir()
            if file_ct >= MAX_FILE_CT:
                solara.Error(f"Too many files in directory unable to offer download ({file_ct} > {MAX_FILE_CT})")
            else:
                solara.Info(f"You selected directory for download as zip: {path}")
                # solara.Button("Download Directory From DBFS", on_click=download_dir)
                zip_name = path.name + ".zip"
                solara.FileDownload(lambda: download_dir(), zip_name, label=f"Download {file_ct} files in "
                                                                            f"{zip_name} From DBFS")

        solara.FileBrowser(
            directory,
            filter=filter_path,
            on_path_select=on_path_select,
            on_file_open=set_file,
            can_select=True,
        ).key("file-browser")


@solara.component
def RootApp():
    with solara.AppBar():
        with solara.AppBarTitle():
            solara.Text(f"Databricks UI Extras: v{databricks_ui_extras.__version__}")
        me = ws_client.current_user.me()
        solara.Text(f"{me.display_name}", style="margin-right: 20px")

    with solara.lab.Tabs():
        with solara.lab.Tab("Workspace Details"):
            with solara.Card("Workspace Info", style="min-width: 500px"):
                solara.Text("Workspace URL: " + ws_client.config.host)
        with solara.lab.Tab("Secrets Manager"):
            SecretsBrowser()

        with solara.lab.Tab("File Exporters"):
            with solara.Card("File Exporters"):
                with solara.lab.Tabs():
                    if os.path.exists("/dbfs"):
                        with solara.lab.Tab("DBFS Root"):
                            with solara.Card("DBFS File Browser (Double click to navigate)"):
                                FileBrowser("/dbfs", )
                        with solara.lab.Tab("FileStore "):
                            with solara.Card("FileStore File Browser (Double click to navigate)"):
                                FileBrowser("/dbfs/FileStore")
                    with solara.lab.Tab("Driver Root"):
                        with solara.Card("Driver File Browser (Double click to navigate)"):
                            FileBrowser("/", exclude_prefixes=["/dbfs"])
                    with solara.lab.Tab("Driver User Home"):
                        with solara.Card("Driver User Home File Browser (Double click to navigate)"):
                            FileBrowser(os.path.expanduser("~/"))
