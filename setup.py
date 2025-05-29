from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="otel_rezervasyon_sistemi",
    version="1.0.0",
    author="[Ad Soyad]",
    author_email="BURAYA_EMAIL_ADRESINIZI_EKLEYIN",  # Kendi e-posta adresinizi girin
    description="Modern ve kullanıcı dostu bir otel rezervasyon sistemi",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kullaniciadi/otel-rezervasyon-sistemi",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "Framework :: Flask",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    include_package_data=True,
    package_data={
        "": ["templates/*", "static/*", "static/css/*", "static/js/*", "static/img/*"],
    },
    entry_points={
        "console_scripts": [
            "otel-rezervasyon=app:main",
        ],
    },
) 