import setuptools

setuptools.setup(
    name="graphiql_sphinx",
    version="0.0.1",
    author="Tirth Shah",
    author_email="tirths@york.ie",
    description="Sphinx extension for Executable Playground for GraphQL APIs",
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'sphinx',
        'fett',
        'graphql-core'
    ],
    package_data={
        'graphiql_sphinx': ['static/*', 'static/graphiql/*'],
    },
    entry_points={
        'sphinx.extensions': [
            'graphiql_sphinx = graphiql_sphinx',
        ],
    },
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    )
)