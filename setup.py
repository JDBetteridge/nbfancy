#import sys
#from nbfancy import configure
import setuptools

# Long description comes from README file
with open('README.md', 'r') as fh:
    long_description = fh.read()

# When installing need to change setting in IPython and Jupyter
# Since this affects users global config, this will now be handled
# post install
#if 'install' in sys.argv:
#    configure.ipython()
#    configure.jupyter()

setuptools.setup(
    name='nbfancy',
    version='0.1dev2',
    author='Jack Betteridge',
    packages=setuptools.find_packages(),
    package_data = {
        'nbfancy/config'    : ['*.ipynb', '*.cfg'],
        'nbfancy/tools'     : ['custom.css'],
        'nbfancy/tools/css' : ['*']
    },
    include_package_data=True,
    py_modules=['configure'],
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
    url='https://github.com/JDBetteridge/nbfancy',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX :: Linux',
    ],
)
