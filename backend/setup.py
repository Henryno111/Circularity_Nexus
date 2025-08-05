#!/usr/bin/env python3
"""
Setup configuration for Circularity Nexus Backend
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="circularity-nexus-backend",
    version="1.0.0",
    author="Circularity Nexus Team",
    author_email="dev@circularitynexus.io",
    description="Waste-to-Wealth Tokenization Platform Backend",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/circularitynexus/core",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
        "ai": [
            "tensorflow>=2.13.0",
            "torch>=2.0.0",
            "torchvision>=0.15.0",
            "opencv-python>=4.8.0",
            "pillow>=10.0.0",
        ],
        "blockchain": [
            "web3>=6.0.0",
            "hedera-sdk-python>=2.0.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "circularity-api=circularity_nexus.main:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
