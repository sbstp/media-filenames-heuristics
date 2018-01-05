import jinja2

from .languages import get_code
from .util import humanize_size


def generate_scan_report(root, movies, target='output.html'):
    movies = list(sorted(movies, key=lambda m: m.title[0]))

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
    with open(target, 'w') as f:
        f.write(tpl.render(root=root, movies=movies))
