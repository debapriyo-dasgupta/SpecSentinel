"""
SpecSentinel - Agentic AI API Health, Compliance & Governance Bot
Setup configuration for package installation
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="specsentinel",
    version="1.0.0",
    author="IBM Hackathon Team",
    description="Agentic AI API Health, Compliance & Governance Bot using Vector DB",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/SpecSentinel_IBM_Hackathon",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Software Development :: Testing",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.11",
    install_requires=[
        "chromadb>=0.5.0",
        "requests>=2.31.0",
        "beautifulsoup4>=4.12.0",
        "lxml>=5.0.0",
        "pyyaml>=6.0",
        "fastapi>=0.110.0",
        "uvicorn[standard]>=0.29.0",
        "python-multipart>=0.0.9",
        "APScheduler>=3.10.0",
        "python-dateutil>=2.9.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
        "ai": [
            "openai>=1.12.0",
            "anthropic>=0.18.0",
            "ibm-watsonx-ai>=1.0.0",
            "google-generativeai>=0.3.0",
        ],
        "ai-openai": ["openai>=1.12.0"],
        "ai-anthropic": ["anthropic>=0.18.0"],
        "ai-watsonx": ["ibm-watsonx-ai>=1.0.0"],
        "ai-google": ["google-generativeai>=0.3.0"],
    },
    entry_points={
        "console_scripts": [
            "specsentinel-api=src.api.app:main",
            "specsentinel-test=tests.test_pipeline:main",
            "specsentinel-scheduler=src.vectordb.ingest.scheduler:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.json", "*.yaml", "*.yml"],
    },
    zip_safe=False,
    keywords=[
        "api",
        "openapi",
        "swagger",
        "governance",
        "compliance",
        "security",
        "vector-database",
        "chromadb",
        "ai",
        "agentic-ai",
    ],
    project_urls={
        "Documentation": "https://github.com/yourusername/SpecSentinel_IBM_Hackathon/blob/main/docs/README.md",
        "Source": "https://github.com/yourusername/SpecSentinel_IBM_Hackathon",
        "Tracker": "https://github.com/yourusername/SpecSentinel_IBM_Hackathon/issues",
    },
)

# Made with Bob
