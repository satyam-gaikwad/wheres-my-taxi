from setuptools import setup, find_packages

setup(
    name='wheres_my_taxi',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'numpy',
        'pandas',
        'scikit-learn',
        'joblib',
        'pyarrow',
    ],
    entry_points={
        'console_scripts': [
            'wheres-my-taxi=scripts.run_pipeline:main',
        ],
    },
) 