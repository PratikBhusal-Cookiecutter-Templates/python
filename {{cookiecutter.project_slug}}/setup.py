#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
from glob import iglob
from os.path import basename, splitext

from setuptools import find_packages, setup  # type: ignore

with open("README.markdown", encoding='utf-8') as f:
    long_description: str = f.read()
    print(long_description)

{%- set license_classifiers = {
    "MIT License": "License :: OSI Approved :: MIT License",
    "Apache 2.0 License": "License :: OSI Approved :: Apache Software License",
} %}

setup(
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
    {%- if cookiecutter.license in license_classifiers %}
        "{{ license_classifiers[cookiecutter.license] }}",
    {%- endif %}
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
{%- if cookiecutter.license in license_classifiers %}
    license="{{ cookiecutter.license }}",
{%- endif %}
{%- if "None" not in cookiecutter.command_line_interface %}
    entry_points={
        "console_scripts": [
            "{{ cookiecutter.project_slug }}={{ cookiecutter.project_slug }}.cli:main",
        ],
    },
{%- endif %}
{%- if cookiecutter.command_line_interface|lower == "click" %}
    install_requires=["click"],
{%- endif %}
    author="",
    author_email='',
    description="",
    include_package_data=True,
    keywords="",
    long_description_content_type='text/markdown',
    long_description=long_description,
    name="",
    package_dir={"": "src"},
    packages=find_packages("src"),
    py_modules=[splitext(basename(path))[0] for path in iglob("src/*.py")],
    python_requires=">=3.6",
    test_suite="tests",
    url="",
    version="0.0.0",
    zip_safe=False,
)
