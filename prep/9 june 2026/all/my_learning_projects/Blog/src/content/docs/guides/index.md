---
title: Guides Overview
description: In-depth guides for advanced usage
order: 1
---

# Guides

Welcome to the guides section! Here you'll find in-depth tutorials for advanced usage of the documentation engine.

## Available Guides

### Content Management

Learn how to organize and structure your documentation:

- Creating nested sections
- Using frontmatter effectively
- Adding images and media
- Code syntax highlighting

### Customization

Customize the look and feel of your documentation:

- Theming with Tailwind CSS
- Custom components
- Adding search functionality
- Integrating analytics

### Deployment

Deploy your documentation to production:

- Cloudflare Pages setup
- GitHub Pages deployment
- Custom domain configuration
- CDN optimization

## Best Practices

### Writing Good Documentation

1. **Be concise** - Get to the point quickly
2. **Use examples** - Show, don't just tell
3. **Stay consistent** - Use the same terminology throughout
4. **Keep it updated** - Outdated docs are worse than no docs

### Organizing Content

```
docs/
├── getting-started/     # For new users
│   ├── index.md
│   ├── install.md
│   └── quickstart.md
├── guides/              # In-depth tutorials
│   ├── index.md
│   └── advanced.md
├── api/                 # API reference
│   └── index.md
└── examples/            # Code examples
    └── index.md
```

### Using Code Blocks

Always specify the language for syntax highlighting:

```javascript
// JavaScript example
function greet(name) {
  return `Hello, ${name}!`;
}
```

```python
# Python example
def greet(name):
    return f"Hello, {name}!"
```

## Next Steps

Explore the [advanced guide](/docs/guides/advanced) for more customization options.
