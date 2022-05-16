from setuptools import find_packages, setup

from src.cli import semver

with open("requirements.txt") as f:
    required = f.read().splitlines()


setup(
    name="serene",
    version=semver,
    description="common seo operations",
    author="wttrz",
    install_requires=required,
    packages=find_packages(),
    entry_points={"console_scripts": ["serene=src.cli:main"]},
)
