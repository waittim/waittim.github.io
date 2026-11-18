# frozen_string_literal: true

# Markdown copies for agents and answer engines.
#
# /llms.txt is the site index. Pages whose URL ends in "/" also get index.md,
# which is the target of rel="alternate" type="text/markdown". GitHub Pages
# does not load plugins, so the files are written into the source tree and
# published as static files. jekyll build refreshes them from posts and pages.
# The HTML layouts are left unchanged.

module Jekyll
  class LlmMarkdownGenerator < Generator
    safe true
    priority :low

    RELATIVE_URL = /\{\{\s*(["'])([^"']+)\1\s*\|\s*relative_url\s*\}\}/.freeze

    def generate(site)
      documents = {
        "llms.txt" => llms_txt(site),
        "index.md" => home_markdown(site),
        "about/index.md" => about_markdown(site),
        "tags/index.md" => tags_markdown(site),
        "search/index.md" => search_markdown(site),
      }
      site.posts.docs.each do |post|
        documents[source_key(post.url)] = post_markdown(site, post)
      end

      written = documents.count { |key, content| write_source(site, key, content) }
      Jekyll.logger.info "LLM Markdown:", "#{documents.length} files (#{written} updated)"
      replace_static_files(site, documents)
    end

    private

    def llms_txt(site)
      lines = []
      lines << "# #{site.config["title"]}"
      lines << ""
      lines << "> #{one_line(site.config["description"])} Projects and opinions " \
               "published here are independent of Zekun Wang’s work at Indeed."
      lines << ""
      lines << "Each link below is the Markdown version of a page. The human page " \
               "is the same path without `index.md`. `/search.json` is a lookup " \
               "index of titles, descriptions, tags, dates, and the first 400 words."
      lines << ""
      lines << "- Author: #{site.config["author_name"]}"
      lines << "- Language: en"
      lines << "- Site: #{absolute(site, "/")}"
      lines << "- Search: #{absolute(site, "/search/")}?q={query}"
      lines << "- Current topics: #{Array(site.config["current_topics"]).join(", ")}"
      lines << ""
      lines << "## Pages"
      lines << ""
      lines << link_line("Home", absolute(site, "/index.md"), "Every post, newest first")
      lines << link_line("About", absolute(site, "/about/index.md"), page_description(site, "about"))
      lines << link_line("Tags", absolute(site, "/tags/index.md"), page_description(site, "tags"))
      lines << link_line("Search", absolute(site, "/search/index.md"), page_description(site, "search"))
      lines << ""

      series_names(site).each do |name|
        lines << "## #{name}"
        lines << ""
        series_posts(site, name).each do |post|
          lines << link_line(post.data["title"], absolute(site, markdown_path(post.url)), post_note(post))
        end
        lines << ""
      end

      unseriesed = site.posts.docs
        .select { |post| post.data["series"].to_s.empty? }
        .sort { |left, right| right <=> left }
      unless unseriesed.empty?
        lines << "## Writing"
        lines << ""
        unseriesed.each do |post|
          lines << link_line(post.data["title"], absolute(site, markdown_path(post.url)), post_note(post))
        end
        lines << ""
      end

      lines << "## Optional"
      lines << ""
      Array(site.config["profiles"]).each do |profile|
        href = profile["href"].to_s
        next unless href.include?("://") || href == "/feed.xml"
        url = href.include?("://") ? href : absolute(site, href)
        note = href.end_with?("/feed.xml") ? "Summaries of the 20 newest posts" : nil
        lines << link_line(profile["title"], url, note)
      end
      Array(site.config["elsewhere"]).each do |item|
        lines << link_line(item["title"], item["href"], nil)
      end
      lines << link_line("Search index", absolute(site, "/search.json"), "First 400 words of each post, plus canonical and Markdown URLs")
      lines << link_line("Sitemap", absolute(site, "/sitemap.xml"), "HTML URLs for search engines")
      lines << ""
      lines.join("\n")
    end

    def home_markdown(site)
      lines = []
      lines << "# #{site.config["title"]}"
      lines << ""
      lines << "> #{one_line(site.config["description"])}"
      lines << ""
      lines << "The HTML homepage shows the latest posts. This file lists every post. " \
               "The grouped agent index is #{absolute(site, "/llms.txt")}."
      lines << ""
      lines << "## Posts"
      lines << ""
      site.posts.docs.sort { |left, right| right <=> left }.each do |post|
        lines << link_line(post.data["title"], absolute(site, markdown_path(post.url)), post_note(post))
      end
      lines << ""
      lines.join("\n")
    end

    def about_markdown(site)
      page = find_page(site, "about")
      lines = []
      lines << "# #{page.data["title"]}"
      lines << ""
      lines << "> #{one_line(page.data["description"])}"
      lines << ""
      lines << "Canonical: #{absolute(site, page.url)}"
      lines << ""
      lines << render_page_body(site, page).strip
      lines << ""
      lines.join("\n")
    end

    def tags_markdown(site)
      page = find_page(site, "tags")
      lines = []
      lines << "# #{page.data["title"]}"
      lines << ""
      lines << "> #{one_line(page.data["description"])}"
      lines << ""
      lines << "Canonical: #{absolute(site, page.url)}"
      lines << ""
      ordered_tags(site).each do |name, posts|
        lines << "## #{name}"
        lines << ""
        posts.each do |post|
          lines << link_line(post.data["title"], absolute(site, markdown_path(post.url)), post.date.strftime("%Y-%m-%d"))
        end
        lines << ""
      end
      lines.join("\n")
    end

    def search_markdown(site)
      page = find_page(site, "search")
      index_url = absolute(site, "/search.json")
      query_url = "#{absolute(site, page.url)}?q={query}"
      <<~MARKDOWN
        # #{page.data["title"]}

        > #{one_line(page.data["description"])}

        Canonical: #{absolute(site, page.url)}

        The human page reads the `q` query parameter and matches it in the browser. An agent can skip that page and use the index directly.

        - Query URL: #{query_url}
        - Index: #{index_url}

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
      MARKDOWN
    end

    def post_markdown(site, post)
      body = expand_relative_urls(site, post.content.to_s.dup)
      if body.include?("relative_url")
        raise "Unresolved relative_url in #{post.relative_path}"
      end

      lines = []
      lines << "# #{one_line(post.data["title"])}"
      lines << ""
      subtitle = one_line(post.data["subtitle"])
      lines << subtitle unless subtitle.empty?
      lines << "" unless subtitle.empty?
      description = one_line(post.data["description"])
      unless description.empty? || description == subtitle
        lines << "> #{description}"
        lines << ""
      end
      lines << "- Canonical: #{absolute(site, post.url)}"
      lines << "- Published: #{iso_date(post.date)}"
      updated = iso_date(post.data["updated"])
      lines << "- Updated: #{updated}" if updated && updated != iso_date(post.date)
      lines << "- Author: #{post.data["author"] || site.config["author_name"]}"
      tags = Array(post.data["tags"])
      lines << "- Tags: #{tags.join(", ")}" unless tags.empty?
      series = post.data["series"].to_s
      unless series.empty?
        siblings = series_posts(site, series)
        index = siblings.index { |item| item.url == post.url }
        lines << "- Series: #{series}, part #{index + 1} of #{siblings.length}" if index
      end
      lines << ""
      lines << body.strip
      lines << ""
      lines.concat(series_section(site, post))
      lines.concat(related_section(site, post))
      lines.concat(adjacent_lines(site, post))
      "#{lines.join("\n").rstrip}\n"
    end

    def series_section(site, post)
      series = post.data["series"].to_s
      return [] if series.empty?
      siblings = series_posts(site, series)
      return [] if siblings.length < 2

      lines = ["", "## #{series}", ""]
      siblings.each do |item|
        label = item.data["series_nav_title"] || item.data["title"]
        if item.url == post.url
          lines << "- #{one_line(label)} (this page)"
        else
          lines << link_line(label, absolute(site, markdown_path(item.url)), nil)
        end
      end
      lines
    end

    # Same selection as _includes/related-posts.html: up to three posts that
    # share the most tags, newest first on a tie, skipping the same series.
    def related_section(site, post)
      tags = Array(post.data["tags"])
      return [] if tags.empty?
      series = post.data["series"]
      ranked = []
      site.posts.docs.sort { |left, right| right <=> left }.each_with_index do |candidate, index|
        next if candidate.url == post.url
        next if series && candidate.data["series"] == series
        shared = (Array(candidate.data["tags"]) & tags).length
        next if shared.zero?
        ranked << [-shared, index, candidate]
      end
      picks = ranked.sort_by { |score, index, _candidate| [score, index] }.first(3)
      return [] if picks.empty?

      lines = ["", "## Related", ""]
      picks.each do |_score, _index, candidate|
        lines << link_line(candidate.data["title"], absolute(site, markdown_path(candidate.url)), candidate.data["description"])
      end
      lines
    end

    def adjacent_lines(site, post)
      lines = [""]
      older = post.previous_doc
      newer = post.next_doc
      lines << "Older: #{md_link(older.data["title"], absolute(site, markdown_path(older.url)))}" if older
      lines << "Newer: #{md_link(newer.data["title"], absolute(site, markdown_path(newer.url)))}" if newer
      lines.length == 1 ? [] : lines
    end

    def render_page_body(site, page)
      payload = {
        "site" => site.site_payload["site"],
        "page" => page.to_liquid,
        "content" => page.content,
      }
      info = {
        :registers => { :site => site, :page => payload["page"] },
        :strict_filters => site.config["liquid"]["strict_filters"],
        :strict_variables => site.config["liquid"]["strict_variables"],
      }
      site.liquid_renderer.file(page.relative_path).parse(page.content.to_s.dup).render!(payload, info)
    end

    def expand_relative_urls(site, content)
      base = site.baseurl.to_s.sub(%r{/\z}, "")
      content.gsub(RELATIVE_URL) do
        path = Regexp.last_match(2)
        path.start_with?("/") ? "#{base}#{path}" : "#{base}/#{path}"
      end
    end

    def ordered_tags(site)
      site.tags.map do |name, posts|
        latest = posts.max_by(&:date)
        [name, posts, latest.date.to_i, posts.length]
      end.sort_by { |name, _posts, epoch, count| [-epoch, -count, name] }
        .map { |name, posts, _epoch, _count| [name, posts] }
    end

    def series_names(site)
      names = site.posts.docs.map { |post| post.data["series"] }.compact.uniq
      names.sort_by do |name|
        latest = series_posts(site, name).max_by(&:date)
        [-latest.date.to_i, name]
      end
    end

    def series_posts(site, name)
      posts = site.posts.docs.select { |post| post.data["series"] == name }
      if posts.any? { |post| post.data["series_order"] }
        posts.sort_by { |post| [post.data["series_order"].to_i, post.date, post.relative_path] }
      else
        posts.sort_by { |post| [post.date, post.relative_path] }
      end
    end

    def iso_date(value)
      return nil if value.nil? || value.to_s.strip.empty?
      value.respond_to?(:strftime) ? value.strftime("%Y-%m-%d") : value.to_s[0, 10]
    end

    def post_note(post)
      note = iso_date(post.date)
      updated = iso_date(post.data["updated"])
      note = "#{note}, updated #{updated}" if updated && updated != note
      description = one_line(post.data["description"])
      description.empty? ? note : "#{note}. #{description}"
    end

    def page_description(site, basename)
      one_line(find_page(site, basename).data["description"])
    end

    def find_page(site, basename)
      site.pages.find { |page| page.basename == basename } ||
        raise("Missing page #{basename}")
    end

    def markdown_path(url)
      directory = url.end_with?("/") ? url : "#{url}/"
      "#{directory}index.md"
    end

    def source_key(url)
      markdown_path(url).sub(%r{\A/}, "")
    end

    def absolute(site, path)
      "#{site.config["url"].to_s.sub(%r{/\z}, "")}#{path.start_with?("/") ? path : "/#{path}"}"
    end

    def link_line(title, url, note)
      line = "- #{md_link(title, url)}"
      text = one_line(note)
      text.empty? ? line : "#{line}: #{text}"
    end

    def md_link(title, url)
      label = one_line(title).gsub("\\", "\\\\").gsub("[", "\\[").gsub("]", "\\]")
      label = url if label.empty?
      "[#{label}](#{url})"
    end

    def one_line(text)
      text.to_s.gsub(/\s+/, " ").strip
    end

    def write_source(site, key, content)
      path = File.expand_path(key, site.source)
      root = File.expand_path(site.source) + File::SEPARATOR
      unless path.start_with?(root)
        raise ArgumentError, "Refusing to write #{path}"
      end
      body = content.end_with?("\n") ? content : "#{content}\n"
      current = File.exist?(path) ? File.read(path, encoding: "UTF-8") : nil
      return false if current == body
      FileUtils.mkdir_p(File.dirname(path))
      File.write(path, body, encoding: "UTF-8")
      true
    end

    def replace_static_files(site, documents)
      site.static_files.delete_if { |file| documents.key?(static_key(file)) }
      documents.each do |key, content|
        site.static_files << GeneratedMarkdownFile.new(site, key, content)
      end
    end

    def static_key(file)
      file.relative_path.to_s.tr("\\", "/").sub(%r{\A\./}, "").sub(%r{\A/}, "")
    end
  end

  class GeneratedMarkdownFile < StaticFile
    def initialize(site, key, content)
      directory = File.dirname(key)
      directory = "" if directory == "."
      super(site, site.source, directory, File.basename(key))
      @generated_content = content.end_with?("\n") ? content : "#{content}\n"
    end

    def modified?
      true
    end

    def write(dest)
      dest_path = destination(dest)
      FileUtils.mkdir_p(File.dirname(dest_path))
      File.write(dest_path, @generated_content, encoding: "UTF-8")
      true
    end
  end
end
