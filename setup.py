from setuptools import setup, find_packages

setup(
    name="abstra_notas",
    version="0.1.0",
    description="Biblioteca de emissão de notas fiscais eletrônicas para empresas brasileiras.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Abstra",
    author_email="notas@abstra.app",
    url="https://github.com/anstra-app/abstra_notas",
    packages=find_packages(),
    install_requires=[
        # Adicione aqui as dependências da sua biblioteca
        # Exemplo: "requests>=2.25.1"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)