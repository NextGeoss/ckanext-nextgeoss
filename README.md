[![Travis](https://travis-ci.org/NextGeoss/ckanext-nextgeoss.svg?branch=master)](https://travis-ci.org/NextGeoss/ckanext-nextgeoss)

[![Coveralls](https://coveralls.io/repos/NextGeoss/ckanext-nextgeoss/badge.svg)](https://coveralls.io/r/NextGeoss/ckanext-nextgeoss)

# ckanext-nextgeoss

This extension includes the theme for the NextGEOSS data hub. The customizations include:

- A custom homepage
- Single-column layouts for the dataset, resource, group, and organization pages
- Renaming groups to topics
- Renaming organizations to providers
- Adding some static pages for the privacy policy, etc.
- Custom design (icons, colors, styles, etc.)
- "Dataset cards" for presenting search results
- "Resource cards" for presenting resources

This extension also adds an itegration with [NiMMbus](https://www.opengis.uab.cat/nimmbus) for submitting and displaying "community feedback" (comments + ratings + additional contextual information) about individual datasets. The feedack is created on and hosted by NiMMbus.

All of the changes and customizations mentioned above are contained in the NextGEOSSPlugin plugin (usable as `nextgeoss` in your .ini file).

The NiMMbus functionality can be broken out into a separate plugin.

## Development Installation

To install ckanext-nextgeoss for development, activate your CKAN virtualenv and
do:

```
git clone https://github.com/nextgeoss/ckanext-nextgeoss.git
cd ckanext-nextgeoss
python setup.py develop
pip install -r dev-requirements.txt
```

## Running the Tests

To run the tests, do:

```
nosetests --nologcapture --with-pylons=test.ini
```

To run the tests and produce a coverage report, first make sure you have
coverage installed in your virtualenv (`pip install coverage`) then run:

```
nosetests --nologcapture --with-pylons=test.ini --with-coverage --cover-package=ckanext.nextgeoss --cover-inclusive --cover-erase --cover-tests
```
