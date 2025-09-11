/* Client-side renderer for Blogs page */
(function () {
  function el(tag, attrs = {}, children = []) {
    const node = document.createElement(tag);
    Object.entries(attrs).forEach(([k, v]) => {
      if (k === 'class') node.className = v;
      else if (k === 'html') node.innerHTML = v;
      else if (k === 'text') node.textContent = v;
      else node.setAttribute(k, v);
    });
    children.forEach(c => node.appendChild(c));
    return node;
  }

  function formatDate(s) {
    if (!s) return '';
    try {
      const d = new Date(s);
      return d.toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: '2-digit' });
    } catch (_) { return s; }
  }

  function render(posts) {
    const container = document.getElementById('blog-list');
    if (!container) return;
    container.innerHTML = '';

    if (!posts || posts.length === 0) {
      container.appendChild(
        el('p', { class: 'col-12', text: 'No blog posts yet. Check back soon!' })
      );
      return;
    }

    // Sort by date desc if dates present
    posts.sort((a, b) => new Date(b.date || '1970-01-01') - new Date(a.date || '1970-01-01'));

    posts.forEach(p => {
      const imgSrc = p.image || 'images/thumbs/resume.png';
      const article = el('article', { class: 'col-6 col-12-xsmall work-item' });
      const link = el('a', {
        href: p.url || '#',
        target: '_blank',
        rel: 'noopener',
        class: 'image fit thumb'
      }, [el('img', { src: imgSrc, alt: p.title || 'Blog post' })]);

      const titleLink = el('a', {
        href: p.url || '#',
        target: '_blank',
        rel: 'noopener',
        text: p.title || 'Untitled'
      });
      const title = el('h3', {}, [titleLink]);
      const meta = [p.source ? p.source : null, p.date ? formatDate(p.date) : null]
        .filter(Boolean)
        .join(' • ');
      const desc = el('p', { text: p.summary ? p.summary : '' });
      const metaEl = meta ? el('p', { class: 'meta', text: meta }) : null;

      article.appendChild(link);
      article.appendChild(title);
      if (metaEl) article.appendChild(metaEl);
      if (desc.textContent) article.appendChild(desc);
      container.appendChild(article);
    });
  }

  function init() {
    fetch('data/blogs.json', { cache: 'no-cache' })
      .then(r => r.json())
      .then(render)
      .catch(() => {
        // Graceful fallback
        render([]);
      });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
