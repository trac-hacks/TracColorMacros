from genshi.builder     import tag
from trac.core          import *
from trac.resource      import *

from trac.wiki.macros import WikiMacroBase

from tracadvparseargs import *

from colormacro import *

class ColorMacroBase(WikiMacroBase):

  reg_table  = []
  reg_table.append({
    'type': 'long_hex',
    're': r"^#[a-f0-9]{6}",
  })

  reg_table.append({
    'type': 'short_hex',
    're': r"^#[a-f0-9]{3}",
  })

  reg_table.append({
    'type': 'rgb',
    're':  r"(rgb\(\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})\s*\))",
  })

  def _hex2rgb(self,c):
    split = (c[0:2], c[2:4], c[4:6])
    return [int(x, 16) for x in split]


  def _parse_arguments(self, content):
    content = content.rstrip().replace('\n', ',')
    largs = parse_args(content, strict=False, listonly=True)
    colors = []
    for line in largs:
      colors.append(self._parse_colorline(line))

    return colors

  def _parse_colorline(self, line):
    raise NotImplementedError('Method not implemented')

  def _parse_color(self,c):
    import re
    re_color = {}
    re_color['orig'] = c.strip()
    re_color['type'] = 'unmatched'

    for reg in self.reg_table:
      expr = reg['expr'] if ('expr' in reg) else re.compile(reg['re'], re.I)
      m = expr.match(c);
      if m:
        re_color['m'] = m
        re_color['type'] = reg['type']

        break

    if re_color['type'] == 'long_hex':
      re_color['hex'] = u'' + re_color['m'].group()
      re_color['rgb'] = self._hex2rgb(re_color['hex'][1:])
    elif re_color['type'] == 'short_hex':
      re_color['hex'] = u'#' + c[1:2] * 2 + c[2:3] * 2 + c[3:4] * 2
      re_color['rgb'] = self._hex2rgb(re_color['hex'][1:])
    elif re_color['type'] == 'rgb':
      re_color['rgb'] = [int(x) for x in (re_color['m'].group(2), re_color['m'].group(3), re_color['m'].group(4))]
      re_color['hex'] = '#%02x%02x%02x' % (re_color['rgb'][0], re_color['rgb'][1], re_color['rgb'][2])

    del(re_color['m'])
    re_color['rgbp'] = u'rgb(%d,%d,%d)' % (re_color['rgb'][0], re_color['rgb'][1], re_color['rgb'][2])

    return re_color


class ColorGradientMacro(ColorMacroBase):
  """
  Create a color gradient table from supplied arguments

  Example:

  {{{
  [[ColorGradient(#00ff00, #ff0000, #0000ff)]]
  }}}

  [[ColorGradient(#00ff00, #ff0000, #0000ff)]]
  ----

  {{{
  {{{#!ColorGradient title="Your title / description"
  #00ff00
  rgb(255\,0\,0)
 "rgb(255, 255, 0)"
  #00f
  }}}
  }}}

  {{{#!ColorGradient title="Your title / description"
  #00ff00
  rgb(255\,0\,0)
 "rgb(255, 255, 0)"
  #00f
  }}}

  """

  def _parse_colorline(self,c):
    cargs = parse_args(c.strip(), listonly=True, delim=' ', )
    c1 = cargs[0]
    color = self._parse_color(c1)
    return color

  def _create_gradient(self,firstcolor, lastcolor):
    
    values = {
      'firstcolor': firstcolor['hex'],
      'lastcolor': lastcolor['hex']
    }
    
    styleblock = """
    filter: progid:DXImageTransform.Microsoft.gradient(startColorstr="%(firstcolor)s", endColorstr="%(lastcolor)s");
    background: -webkit-gradient(linear, left top, left bottom, from(%(firstcolor)s), to(%(lastcolor)s));
    background: -moz-linear-gradient(top,  %(firstcolor)s,  %(lastcolor)s);
    """ % values
    
    return tag.td(style=styleblock.replace('\n', ''), colspan="2", class_='colorgradient');

  def expand_macro(self, formatter, name, content, args):
    title = 'Color Gradient'
    if args and 'title' in args:
      title = args['title']

    colors = self._parse_arguments(content)

    lastcolor = {}
    tbody = []

    for color in colors:
      if 'orig' in lastcolor:
        tbody.append(self._create_gradient(lastcolor, color))
        
      tbody.append([
        tag.td(
          style='background-color:' + color['orig']
        )(
          tag.div(style='color: black')(color['hex']),
          tag.div(style='color: white')(color['hex'])
        ),
        tag.td(
          style='background-color:' + color['orig']
        )(
          tag.div(style='color: black')(color['rgbp']),
          tag.div(style='color: white')(color['rgbp'])
        )
      ])

      lastcolor = color

    ## end for loop

    if len(tbody) > 0:
      
      table = tag.table(class_='colorgradient')
      table()(tag.thead()(tag.th(colspan="2")(title)))
     
      table()(tag.tbody(class_='colorgradient')([tag.tr()(td) for td in tbody]))

      return table;
    else:
      return tag.div(class_='colorgradient')('Nothing to display')


class ColorSchemeMacro(ColorMacroBase):
  """
  Creates a color scheme from supplied arguments

  Example:

  {{{
  [[ColorScheme(#00ff00, #ff0000, #0000ff)]]
  }}}

  [[ColorScheme(#00ff00, #ff0000, #0000ff)]]

  ----

  {{{
  {{{#!ColorScheme
  #00ff00 green
  rgb(255\,0\,0) red
 "rgb(255, 255, 0)" Your title / description
  #00f
  }}}
  }}}

  {{{#!ColorScheme
  #00ff00 green
  rgb(255\,0\,0) red
  "rgb(255, 255, 0)" Your title / description
  #00f
  }}}

  """

  def _parse_colorline(self,c):
    cargs = parse_args(c.strip(), listonly=True, delim=' ', )
    c = cargs[0]

    re_color = self._parse_color(c)
    re_color['title'] = ' '.join(cargs[1:])

    return re_color



  def expand_macro(self, formatter, name, content, args):

    title = 'Color Scheme'
    if args and 'title' in args:
      title = args['title']

    tbody = []
    have_comment = False
    colors = self._parse_arguments(content)

    for color in colors:
      if len(color['title']) > 0:
        have_comment = True
      ## Create row
      tbody.append(
        [
          tag.td()(tag.strong(color['title'])),
          tag.td(
              style='background-color:' + color['orig']
            )(
              tag.div(style='color: black')(color['hex']),
              tag.div(style='color: white')(color['hex'])
          ),
          tag.td(
              style='background-color:' + color['orig']
            )(
              tag.div(style='color: black')(color['rgbp']),
              tag.div(style='color: white')(color['rgbp'])
          ),
        ]
      )
      ## end for loop

    if len(tbody) > 0:
      colcount = len(tbody[0])
      if not have_comment:
        colcount -= 1
      
      table = tag.table(class_='colorscheme')
      table()(tag.thead()(tag.th(colspan='%d' % colcount)(title)))
      ## Attach row in table.
      if have_comment:
        table()(tag.tbody(class_='colorlist')([tag.tr(row) for row in tbody]))
      else:
        table()(tag.tbody(class_='colorlist')([tag.tr(row[1:]) for row in tbody]))

      return table;
    else:
      return tag.div(class_='colorscheme')('Nothing to display')
