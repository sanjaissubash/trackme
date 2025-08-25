from setuptools import setup, find_packages

setup(
    name='trackme',
    version='0.3.0',
    description='TrackMe CLI - final hybrid REPL and one-liner time tracker',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'rich>=13.0.0'
    ],
    entry_points={
        'console_scripts': [
            'trackme=trackme.cli:main',
        ],
    },
    python_requires='>=3.8',
)
