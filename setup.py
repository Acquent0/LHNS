from setuptools import setup, find_packages

setup(
    name="lhns",
    version="1.0",
    author="CIAM Group, SUSTech",
    description="LLM-Driven Neighborhood Search for Efficient Heuristic Design",
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    python_requires=">=3.10",
    install_requires=[
        "numpy",
        "numba",
        "joblib"
    ]
)