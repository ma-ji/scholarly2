import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='scholarly2',
    version='2.0.0',
    author='Ji Ma',
    author_email='ma47@iu.edu',
    description='Simple access to Google Scholar authors and citations',
    long_description=long_description,
    long_description_content_type="text/markdown",
    license='Unlicense',

    url='https://github.com/ma-ji/scholarly2',
    packages=setuptools.find_packages(),
    keywords=['Google Scholar', 'academics', 'citations'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules'],
    install_requires=['arrow',
                      'beautifulsoup4',
                      'bibtexparser',
                      'deprecated',
                      'fake_useragent',
                      'free-proxy',
                      'httpx[socks]',
                      'python-dotenv',
                      'requests[socks]',
                      'selenium',
                      'sphinx_rtd_theme',
                      'typing_extensions'
                      ],
    extras_require={
        'tor': ['stem'],
    },
    test_suite="test_module.py"
)
