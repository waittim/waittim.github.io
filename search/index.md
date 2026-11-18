# Search

> Search posts by title, tags, and content.

Canonical: https://www.zekun.blog/search/

The human page reads the `q` query parameter and matches it in the browser. An agent can skip that page and use the index directly.

- Query URL: https://www.zekun.blog/search/?q={query}
- Index: https://www.zekun.blog/search.json

## search.json

The index is a JSON array, one object per post. `content` is the first 400 words of the article with HTML removed, not the full text. The full text is the `markdown` URL.

- `title`
- `subtitle`
- `description`
- `tags`
- `url`: site-relative HTML URL
- `canonical`: absolute HTML URL
- `markdown`: absolute Markdown URL
- `date`
- `content`

A query matches when every word appears in the combined title, subtitle, description, tags, and content. The human page shows at most 20 matches.
