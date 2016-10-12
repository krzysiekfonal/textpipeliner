from setuptools import setup

setup(name='textpipeliner',
      version='0.2.1',
      description='textpipeliner - library for extracting specific words from sentences of a document',
      long_description='This library allows you to extract specific words(in form of tuple) going through every '
                       'sentence of a document using custom created structure of extraction processing.',
      classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Intended Audience :: Science/Research',
      ],
      keywords='nlp text mining text extraction',
      url='https://github.com/krzysiekfonal/textpipeliner',
      author='Krzysztof Fonal',
      author_email='krzysiek.fonal@gmail.com',
      license='MIT',
      packages=['textpipeliner'],
      install_requires=[
          'spacy', 'grammaregex'
      ],
      test_suite='nose.collector',
      tests_require=['nose'],
      zip_safe=True)
