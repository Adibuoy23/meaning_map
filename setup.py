import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="meaning_map-Adibuoy23",
    version="0.0.1",
    author="Aditya Upadhyayula, Taylor R Hayes, Gwen Rehrig",
    author_email="aditya.usa8@gmail.com",
    description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Adibuoy23/meaning_map",
    project_urls={
        "Bug Tracker": "https://github.com/Adibuoy23/meaning_map/issues",
    },
    classifiers=[
        "Development Status :: 1 - Beta",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=["opencv-python", "numpy", "scipy", "tk",
                      "pandas", "tqdm", "matplotlib", "requests", "natsort", "Pillow"],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)
