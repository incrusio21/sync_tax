from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in sync_tax/__init__.py
from sync_tax import __version__ as version

setup(
	name="sync_tax",
	version=version,
	description="Sync Tax deprint",
	author="DAS",
	author_email="das@gmail.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
