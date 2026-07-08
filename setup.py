from setuptools import find_packages, setup

setup(
    name="django-fusion",
    version="0.1.0",
    package_dir={"": "src"},
    packages=find_packages("src", include=["django_fusion", "django_fusion.*"]),
    include_package_data=True,
    install_requires=["django>=4.2", "wagtail"],
)
