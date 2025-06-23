# setup.py
import setuptools

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setuptools.setup(
    name="mlProject",
    version="0.1.0",
    author="Anand Singh",
    author_email="anandmehta300@gmail.com",
    description="A small python package for ML app",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/anandmehta300/AutoPrice-AI",
    project_urls={
        "Bug Tracker": "https://github.com/anandmehta300/AutoPrice-AI/issues",
    },
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    install_requires=[],  # you can add dependencies here if needed
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
