from setuptools import setup, find_packages

setup(
    name="sc2_bot",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.7",
    install_requires=[
        "sc2>=1.0.0",
        "numpy>=1.20.0",
        "pywin32>=300; platform_system=='Windows'",
    ],
    entry_points={
        "console_scripts": [
            "sc2-bot=scripts.run:main",
        ],
    },
    # Include non-Python files (like configs) from MANIFEST.in
    include_package_data=True,
)
