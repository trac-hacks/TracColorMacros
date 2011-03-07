# To change this template, choose Tools | Templates
# and open the template in the editor.
from trac.core import *
from trac.resource      import *

from trac.web.chrome    import add_stylesheet, ITemplateProvider
from trac.web.api      import IRequestFilter

class ColorScheme(Component):
  """
    Default CSS.
  """
  implements (IRequestFilter, ITemplateProvider)

  def get_templates_dirs(self):
    return []
#    from pkg_resources import resource_filename
#    return [resource_filename(__name__, 'templates')]

  def get_htdocs_dirs(self):
    from pkg_resources import resource_filename
    return [('colormacro', resource_filename(__name__, 'htdocs'))]

  def pre_process_request(self, req, handler):
        return handler

  def post_process_request(self, req, template, data, content_type):
    add_stylesheet( req, 'colormacro/colormacro.css', mimetype='text/css' )
    return (template, data, content_type)
