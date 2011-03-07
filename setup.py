# To change this template, choose Tools | Templates
# and open the template in the editor.
from setuptools import setup

__url__       = "https://github.com/vStone/TracColorMacros"
__author__    = "Jan Vansteenkiste <jan@vstone.eu>"
__date__      = "2011.03.07"

setup(
    name=     'TracColorMacros',
    version=  '0.3',
    packages= ['colormacro'],
    author = 'Jan Vansteenkiste',
    author_email = 'jan@vstone.eu',
    description = 'Trac Color Related Macros.',
    url = 'https://github.com/vStone/TracColorMacros',
    license = 'GPLv3',
    keywords = 'trac macro color',
    package_data={ 'colormacro': [
      'htdocs/*.css'
    ]},
    entry_points = {'trac.plugins': [
      'colormacro.macro = colormacro.macro',
      'colormacro.web_ui = colormacro.web_ui',
    ]},
)
