import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
with open('requirements.txt', 'r', encoding='utf-8') as fh:
    required_packages = list(map(lambda x: x.strip(), fh.readlines()))

setuptools.setup(
    name="inspiring_murdock", # Replace with your own username
    version="0.0.1",
    author="Modhaffer Rahmani",
    author_email="modhaffer.rahmani@gmail.com",
    description="An python invoke based package to manage AWS resources and more",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    install_requires=required_packages,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
