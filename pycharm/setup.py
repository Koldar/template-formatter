import setuptools

import version

with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
    name="template-formatter-Massimo-Bono",
    version=version.VERSION,
    author="Massimo Bono",
    author_email="massimobono1@gmail.com",
    description="Wrapper to jinja2 template system",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/sampleproject",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache 2 License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)
