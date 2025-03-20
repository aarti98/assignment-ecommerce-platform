from setuptools import setup, find_packages

setup(
    name="ecommerce-platform",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.103.1",
        "uvicorn>=0.23.2",
        "sqlalchemy>=2.0.20",
        "pydantic>=2.3.0",
        "pydantic-settings>=2.0.3",
        "pytest>=7.4.2",
    ],
) 