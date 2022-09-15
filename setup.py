import sys

try:
    from setuptools import setup, find_packages
except Exception:
    raise ImportError("setuptools is required to install Earlytool!")
import io
import os

# Package meta-data.
NAME = "Earlytool"
DESCRIPTION = "Earlytool: An Early NIDS"
URL = "https://gitlab.abo.fi/veridevops-public/earlytool"
EMAIL = "tahmad@abo.fi"
AUTHOR = "Tanwir Ahmad"
REQUIRES_PYTHON = ">=3.6.0"
GIT_REPO_LIBS = [
    "cicflowmeter @ git+https://gitlab.abo.fi/tahmad/cicflowmeter-py.git@py36"
]
VERSION = None


def get_requirements(source: str = "requirements.txt"):
    requirements = []
    with open(source) as f:
        for line in f:
            package, _, comment = line.partition("#")
            package = package.strip()
            if package and "git" not in package:
                requirements.append(package)

    return requirements


REQUIRED = get_requirements("requirements.txt")


def get_long_description():
    """Extract description from README.md, for PyPI's usage"""

    def process_ignore_tags(buffer):
        return "\n".join(
            x for x in buffer.split("\n") if "<!-- ignore_ppi -->" not in x
        )

    try:
        fpath = os.path.join(os.path.dirname(__file__), "README.md")
        with io.open(fpath, encoding="utf-8") as f:
            readme = f.read()
            desc = readme.partition("<!-- start_ppi_description -->")[2]
            desc = desc.partition("<!-- stop_ppi_description -->")[0]
            return process_ignore_tags(desc.strip())
    except IOError:
        return None


setup(
    name=NAME,
    version=__import__('early').__version__,
    description=DESCRIPTION,
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    # package_dir={"": "early"},
    packages=find_packages(),
    # Build starting scripts automatically
    entry_points={
        "console_scripts": [
            "early_monitor=monitor:main",
            "early_display=display:main"
        ],
    },
    install_requires=REQUIRED + GIT_REPO_LIBS,
    # dependency_links=DEPENDENCIES,
    include_package_data=True,
    license='Apache',
    project_urls={
        'Source Code': 'https://gitlab.abo.fi/veridevops-public/earlytool/',
    },
    keywords=["network"],
    classifiers=[
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Science/Research",
        "Intended Audience :: System Administrators",
        "Intended Audience :: Telecommunications Industry",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Security",
        "Topic :: System :: Networking",
        "Topic :: System :: Networking :: Monitoring",
    ]
)