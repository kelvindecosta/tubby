"""This module configures the main package"""


from setuptools import find_packages, setup


from src.meta import AUTHOR, DESCRIPTION, LICENSE, NAME, REPO_URL, VERSION


with open("README.md", "r") as fs:
    LONG_DESCRIPTION = fs.read()


setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url=REPO_URL,
    author=AUTHOR,
    author_email="decostakelvin@gmail.com",
    license=LICENSE,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "License :: OSI Approved :: MIT License",
        "Development Status :: 5 - Production/Stable",
        "Topic :: Games/Entertainment :: Role-Playing",
        "Topic :: Terminals",
        "Topic :: Utilities",
    ],
    packages=list(map(lambda x: x.replace("src", NAME), find_packages("."))),
    package_dir={NAME: "src"},
    package_data={"": ["data/*.txt"]},
    python_requires=">=3.9",
    install_requires=[
        "click",
        "bs4",
        "httpx",
        "simple-term-menu",
        "sty",
        "tqdm",
    ],
    entry_points={"console_scripts": [f"{NAME} = {NAME}.__main__:main"]},
)
