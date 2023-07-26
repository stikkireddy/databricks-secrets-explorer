# Databricks notebook source

# COMMAND ----------

# MAGIC %pip install git+https://github.com/stikkireddy/databricks-ui-extras.git@main

# COMMAND ----------

dbutils.library.restartPython()

# COMMAND ----------

from databricks_ui_extras import Page, wire_dbutils_for_ws_client, app

wire_dbutils_for_ws_client(app)

# COMMAND ----------

print("Working on setting up page")

# COMMAND ----------

Page()


