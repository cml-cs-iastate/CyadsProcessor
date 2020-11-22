from setuptools import setup, find_namespace_packages

setup(
    name="CyadsProcessor",
    version="1.32.0",
    description="CyadsProcessor",
    url="https://github.com/cml-cs-iastate/CyadsProcessor",
    license="MIT",
    classifiers=[

        ],
    python_requires=">=3.7",
    install_requires=[
        'django>=3.0',
        "django-extensions>=2.2.9",
        "google-cloud-pubsub>=2.1.0",
        "mysqlclient>=1.4.6",
        "python-dateutil>=2.8.1",
        "google-api-python-client>=1.12.5",
        "requests>=2.25.0",
        "youtube-dl>=2020.11.21.1",
        "beautifulsoup4>=4.9.1",
        "tenacity>=6.2.0",
        "lxml>=4.5.1",
        "html5lib>=1.0.1",
        "gunicorn>=20.0.4",
        "more-itertools>=8.3.0",
        "video_metadata @ git+https://github.com/cml-cs-iastate/video_metadata",
        "structlog==20.1.0",
        "docutils",
    ],
    packages=find_namespace_packages(),
)
