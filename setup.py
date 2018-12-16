import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='nbfancy-tools',
    version='0.1dev',
    author='Jack Betteridge',
    packages=setuptools.find_packages(),
    entry_points={
        'console_scripts': [
            'nbfancy=nbfancy.__main__:main',
        ],
    },
    author_email='J.D.Betteridge@Bath.ac.uk',
    description='Tools for rendering notebooks suitable for teaching',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/JDBetteridge/nbfancy-tools',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Linux',
    ],
)
