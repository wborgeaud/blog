import json

data = json.loads(open('blogdata.json').read())

md = f"""
# {data['blogtitle']}
<div style="text-align: center; color: hsl(0, 0%, 40%);"><h3>
A blog on math, crypto, hacking, coding and more.
</h3></div>



## Posts
"""

posts = data['posts']
posts = sorted(posts, key=lambda k: k['date'], reverse=True)

for post in posts:
    md += f"### [{post['title']}](./posts/{post['path']})\n"

with open('index.md','w') as f:
    f.write(md)
