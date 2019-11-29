# Blog

### Create `index.html`

To create `index.html`, run `python3.7 deploy.py`. It will create `index.md`. Then open it in `Typora` and export as `HTML`.

### Create posts

Write a post in `Markdown` using `Typora`. Then export it as `HTML` and put it in `public/posts`. Finally, update `blogdata.json` with the new post by adding it's title, date and path. Re-create `index.html` and push to Github.  

### Add navbar
To add the navbar to `public/posts/post.html`, run `python add_nav.py public/posts/post.html`.
