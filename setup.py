import sys
import configure
import setuptools

# Long description comes from README file
with open('README.md', 'r') as fh:
    long_description = fh.read()

# When installing need to change setting in IPython and Jupyter
if 'install' in sys.argv:
    configure.ipython()
    configure.jupyter()

setuptools.setup(
    name='nbfancy-tools',
    version='0.1dev0',
    author='Jack Betteridge',
    packages=setuptools.find_packages(),
    py_modules=['configure'],
    ## TODO: replace with a MANIFEST.in
    package_data={
        'nbfancy' : ['tools/custom.css',
                     'tools/css/w3.css',
                     'tools/css/font-awesome.css',
                     'tools/css/fontawesome-webfont.ttf'],
    },
    install_requires = ['ipython>=6','jupyter',],
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
