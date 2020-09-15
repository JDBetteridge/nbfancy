import setuptools

# Long description comes from README file
with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='nbfancy',
    version='0.1a2',
    author='Jack Betteridge',
    packages=setuptools.find_packages(),
    package_data = {
        'nbfancy/config'    : ['*.ipynb', '*.cfg'],
        'nbfancy/tools'     : ['*'],
    },
    include_package_data=True,
    install_requires = ['ipython>=6', 'jupyter',],
    entry_points={
        'console_scripts': [
            'nbfancy=nbfancy.__main__:main',
        ],
    },
    author_email='J.D.Betteridge@Bath.ac.uk',
    description='Tools for rendering notebooks suitable for teaching',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/JDBetteridge/nbfancy',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX :: Linux',
    ],
)
