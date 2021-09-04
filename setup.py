# Automatically created by: shub deploy

from setuptools import setup, find_packages

setup(
    name         = 'top_results',
    version      = '1.0',
    packages     = find_packages(),
    package_data={
        'top_results': ['resources/*.csv']
    },
    entry_points = {'scrapy': ['settings = top_results.settings']},
    zip_safe=False,

)
