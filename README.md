# [zekun.blog](http://zekun.blog)

Personal blog of Zekun Wang.

Blog address: [zekun.blog](https://www.zekun.blog/)

## Local development

This project pins Ruby in `mise.toml`. Install [mise](https://mise.jdx.dev/) once:

```sh
curl https://mise.run | sh
```

Then restart your shell, or add mise to your current shell:

```sh
eval "$(~/.local/bin/mise activate zsh)"
```

Install the project Ruby:

```sh
mise install
```

If you do not activate mise in your shell, use `~/.local/bin/mise` instead of `mise` in the commands below.

Install Ruby dependencies once:

```sh
mise exec -- bundle install
```

Run the site locally:

```sh
mise exec -- bundle exec jekyll serve --livereload
```

Build the site:

```sh
mise exec -- bundle exec jekyll build
```

Styles and theme scripts are checked in for GitHub Pages. After changing files under `less/` or `js/hux-blog.js`, install Node dependencies once, then run `npm run build:assets`. That rebuilds the minified CSS and JS the site actually loads, and rewrites `asset_version` in `_config.yml`:

```sh
npm install
npm run build:assets
```

