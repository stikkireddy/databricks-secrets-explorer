from setuptools import setup, find_packages

setup(
    name='databricks-ui-extras',
    author='Sri Tikkireddy',
    author_email='sri.tikkireddy@databricks.com',
    description='A package for a ui to do misc stuff in databricks',
    use_scm_version={
        "local_scheme": "node-and-timestamp"
    },
    setup_requires=['setuptools_scm'],
    install_requires=[
        "databricks-sdk>=0.2.1, <1.0.0",
        "solara>=1.19.0, <2.0.0",
    ],
    license_files=('LICENSE',),
    classifiers=[
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    keywords='Databricks Clusters',
)
