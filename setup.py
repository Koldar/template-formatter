import os
from typing import List, Tuple, Iterable

import setuptools

from template_formatter import version

with open("README.md", "r") as fh:
    long_description = fh.read()


def get_requirements(requirements: str) -> Iterable[str]:
    with open(requirements, encoding="utf-8", mode="r") as f:
        lines = f.readlines()
    for line in lines:
        yield line.split("==")[0]


def get_data_files() -> List[Tuple[str, List[str]]]:
    if os.name == "nt":
        return [
            # put exe into C:\Python38\Scripts
            ("Scripts", [os.path.join("scripts", "template-formatter.exe")])
        ]
    elif os.name == "posix":
        return [
            # /usr/local/bin
            ("bin", [os.path.join("scripts", "template-formatter")])
        ]
    else:
        raise ValueError(f"invalid os name {os.name}")


setuptools.setup(
    name="template-formatter",
    version=str(version.VERSION),
    author="Massimo Bono",
    author_email="massimobono1@gmail.com",
    description="Wrapper to jinja2 template system",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Koldar/template-formatter.git",
    packages=setuptools.find_packages(),
    scripts=["bin/template-formatter.py"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache 2 License",
        "Operating System :: OS Independent",
    ],
    install_requires=list(get_requirements("requirements.txt")),
    include_package_data=True,
    #data_files=get_data_files(),
    entry_points={"console_scripts": ["template-formatter=template_formatter.main:main"]},
    python_requires='>=3.8',
)
