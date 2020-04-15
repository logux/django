from setuptools import setup, find_packages

from logux import VERSION, AUTHOR

setup(
    name='logux-django',
    version=VERSION,
    packages=find_packages(),
    install_requires=[
        "django>=2.2.12,<3",
        "requests==2.23.0"
    ],
    url='https://github.com/logux/django/',
    license='MIT',
    author=AUTHOR,
    author_email='egregors@pm.me',
    description='Django Logux integration engine https://logux.io/',
    long_description=open('README.md', 'r', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        'Programming Language :: Python :: 3.7'
    ],
)
