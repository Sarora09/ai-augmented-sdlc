from setuptools import setup, find_packages

with open("requirements.txt") as r:
    requirements = r.read().splitlines()

setup(
    name = "AI-AUGMENTED-SDLC",
    version = "0.1",
    author = "Sarora09",
    packages = find_packages(),
    install_requires = requirements,
)