from setuptools import setup

# Metadata goes in setup.cfg. These are here for GitHub's dependency graph.

setup(
    name="mistune",
    package_data={"mistune": ["py.typed", ]}
)
