from setuptools import find_packages, setup

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="blackboxapi",
    version="1.0.0",
    description="API for blackbox",
    package_dir={"": "blackboxapi"},
    package=find_packages(where="blackboxapi"),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/werewoof/blackboxapi",
    author="asianchinaboi",
    license="MIT",
    python_requires=">=3.10"
)
