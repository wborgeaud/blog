import sys
from bs4 import BeautifulSoup
import re

if len(sys.argv) < 2:
    print("Specify a file name")
    sys.exit(0)

fp = sys.argv[1]

ind = open(fp).read()

nav_styles = """

.navbar {
  list-style-type: none;
  margin: 0;
  padding: 0;
  overflow: hidden;
  box-shadow: 0px 1px 3px;
  width: 100vw;
  margin-left: -30px;
}

.navitem {
  float: left;
  white-space: normal !important;
}

.navitemref {
  display: block;
  text-align: center;
  padding: 14px 16px;
  text-decoration: none;
}

.navitemref:hover:not(.active) {
  background-color: hsl(0,0%,95%);
}

"""

nav_bar = """

<ul class="navbar">
  <li class="navitem"><a class="navitemref" href="../../">William Borgeaud's blog</a></li>
</ul>

"""

end_style = ind.find('</style>')
ind = ind[:end_style] +  nav_styles + ind[end_style:]

body = re.search(r"<body.*?>", ind, flags=re.DOTALL).end()
ind = ind[:body] + nav_bar + ind[body:]

with open(fp, 'w') as f:
    f.write(ind)
