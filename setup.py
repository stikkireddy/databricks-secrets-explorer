from setuptools import setup, find_packages

setup(
    name='databricks-secrets-explorer',
    author='Sri Tikkireddy',
    author_email='sri.tikkireddy@databricks.com',
    description='A package for a ui to manipulate secrets',
    packages=find_packages(exclude=['tests']),
    package_data={'': ['infinite_loop_notebook.template']},
    use_scm_version={
        "root": "..",
        "relative_to": __file__,
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
