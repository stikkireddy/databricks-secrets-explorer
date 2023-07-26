# Databricks notebook source

# MAGIC %pip install git+https://github.com/stikkireddy/databricks-ui-extras.git@main

# COMMAND ----------

dbutils.library.restartPython()

# COMMAND ----------

from databricks_ui_extras import Page, wire_dbutils_for_ws_client, app

wire_dbutils_for_ws_client(app, globals())

# COMMAND ----------

print("Working on setting up page")

# COMMAND ----------

Page()


