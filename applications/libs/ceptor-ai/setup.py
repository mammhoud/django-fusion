from setuptools import find_packages, setup

setup(
    name="ceptor-ai",
    version="0.1.0",
    package_dir={"": "src"},
    packages=find_packages("src", include=["ceptor_ai", "ceptor_ai.*"]),
    include_package_data=True,
    install_requires=["django>=4.2", "django-mcp-server>=0.1.0", "watchdog>=4.0"],
    entry_points={"console_scripts": ["ceptor-ai=ceptor_ai.cli:main"]},
)
