"""
Insert datasets into BigQuery database.

The goal of this module is to facilitate loading datasets into BigQuery.
Serialize the output of operations that create resusable datasets in the database.
"""

# project precis-seo sst-306515
# fix authentication via service account

# we could add new clients in some sort of container (list)? and run a handfule of operations.
# (1) keyword research
# - find seed keywords
# - use kwlist tool
# - metrics (???) unclear how to get the metrics we need
# https://cloud.google.com/bigquery/docs/reference/libraries#client-libraries-install-python
# https://googleapis.dev/python/pandas-gbq/latest/index.html
# https://www.rudderstack.com/guides/how-to-access-and-query-your-bigquery-data-using-python-and-r/
