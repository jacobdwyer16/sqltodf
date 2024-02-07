from setuptools import setup, find_packages

setup(
    name='sqltodf',
    version='0.1.0',
    packages=find_packages(),
    url="https://github.com/jacobdwyer16/sqltodf.git",
    author='Jacob Dwyer',
    author_email='jacobdwyer16@gmail.com',
    install_requires=[
        'pandas',
        'polars',
        'jaydebeapi',
        'pyodbc',
        'python-dotenv',
        'pydantic',
        'pytest'
    ],
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
)