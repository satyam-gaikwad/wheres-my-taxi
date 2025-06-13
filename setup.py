from setuptools import setup, find_packages

setup(
    name="wheres-my-taxi",
    version="0.1.0",
    packages=find_packages(include=['utils', 'utils.*']),
    install_requires=[
        "pandas",
        "numpy",
        "scikit-learn",
        "pyarrow",  # for parquet files
    ],
    python_requires=">=3.8",
    author="Satyam Gaikwad",
    author_email="satyam.gaikwad92@gmail.com",
    description="A machine learning project for predicting taxi trip durations",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/satyam-gaikwad/wheres-my-taxi",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        'console_scripts': [
            'wheres-my-taxi=scripts.run_pipeline:main',
        ],
    },
) 