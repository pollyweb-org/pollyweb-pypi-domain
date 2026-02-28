from setuptools import setup, find_packages

setup(
    name="pollyweb-domain",
    version="0.1.1",
    description="Domain manifests and message helpers for PollyWeb.",
    author="jorgemf",
    author_email="pollyweb@pollycore.net",
    license="Apache-2.0",
    url="https://www.pollyweb.org",
    project_urls={
        "Website": "https://www.pollyweb.org",
        "Logo": "https://www.pollyweb.org/images/pollyweb-logo.png",
    },
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    install_requires=[
        "pollyweb-utils",
    ],
    python_requires=">=3.8",
)
