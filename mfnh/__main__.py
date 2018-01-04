import sys
from pathlib import Path

import jinja2
import tmdbsimple as tmdb

from .languages import get_code
from .movies import find_movies
from .util import humanize_size, filter_name

# Borrowing kodi's API key
# ecbc86c92da237cb9faff6d3ddc4be6d

tmdb.API_KEY = 'ecbc86c92da237cb9faff6d3ddc4be6d'


if __name__ == '__main__':
    root = Path(sys.argv[1])
    movies = list(find_movies(root))
    movies.sort(key=lambda m: m.title)

    env = jinja2.Environment()
    env.filters['humanize_size'] = humanize_size
    env.filters['lang_code'] = get_code
    tpl = env.from_string("""\
<html>
<head>
<meta charset="utf-8">
<title>Media Scan Report</title>
<style>
body {
    font-family: monospace;
    font-size: small;
    width: 100%;
}
td {
    white-space: nowrap;
    text-align: left;
}
.right {
    text-align: right;
}
</style>
</head>
<body>
<table border="1">
<thead>
<tr>
<th>Path Title</th>
<th>Subs</th>
<th>Parent Ttitle</th>
<th>Size</th>
<th>Path</th>
<th>Parent</th>
</tr>
</thead>
<tbody>
{% for m in movies %}
<tr>
<td>{{m.title}}</td>
<td>
<ul>
{% for (sub, lang) in m.subs %}
<li>{{lang.name}}({{lang|lang_code}}) - {{sub.relative_to(root)}}</li>
{% endfor %}
</ul>
</td>
<td>{{m.parent_title}}</td>
<td class="right">{{m.size | humanize_size}}</td>
<td>{{m.path.relative_to(root)}}</td>
<td>{% if m.parent %}{{m.parent.relative_to(root)}}{% endif %}</td>
</tr>
{% endfor %}
</tbody>
</table>
</body>
</html>
""")
    with open('output.html', 'w') as f:
        f.write(tpl.render(root=root, movies=movies))

    # print(tmdb.Configuration().info(), file=sys.stderr)

    # for movie in movies[:1]:
    #     search = tmdb.Search()
    #     resp = search.movie(query=movie.title[0], year=movie.title[1])
    #     results = search.results
    #     print(results, file=sys.stderr)
    #     title = search.results[0]['original_title']
    #     year = search.results[0]['release_date'][:4]
    #     print('{} ({})'.format(filter_name(title), year), file=sys.stderr)
