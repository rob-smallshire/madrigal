from pathlib import Path
from setuptools import setup, find_packages


setup(
    name='madrigal',
    version="0.0.0",
    packages=find_packages('source'),

    author='Robert Smallshire',
    author_email='robert@smallshire.org.uk',
    description='Intentional Python Programming',
    license='MIT',
    keywords='',
    url='http://github.com/robsmallshire/madrigal',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3 :: Only',
    ],
    platforms='any',
    include_package_data=True,
    package_dir={'': 'source'},
    # package_data={'madrigal': . . .},
    install_requires=[],
    # List additional groups of dependencies here (e.g. development
    # dependencies). You can install these using the following syntax, for
    # example: $ pip install -e ".[dev,test]"
    extras_require={
        'dev': ['black', 'bump2version'],
        # 'doc': ['sphinx', 'cartouche'],
        'test': ['hypothesis', 'pytest'],
    },
    entry_points={
        # 'console_scripts': [
        #    'madrigal = madrigal.cli:main',
        # ],
    },
    long_description=Path('README.rst').read_text(encoding='utf-8'),
)
