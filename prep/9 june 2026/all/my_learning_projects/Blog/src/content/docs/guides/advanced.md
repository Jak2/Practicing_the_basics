---
title: Advanced Customization
description: Deep dive into advanced customization options
order: 2
---

# Advanced Customization

Take your documentation to the next level with these advanced customization techniques.

## Custom Components

### Creating a Callout Component

You can create reusable callout boxes for important information:

```astro
---
// src/components/Callout.astro
interface Props {
  type?: 'info' | 'warning' | 'error' | 'success';
  title?: string;
}

const { type = 'info', title } = Astro.props;

const styles = {
  info: 'bg-blue-50 border-blue-500',
  warning: 'bg-amber-50 border-amber-500',
  error: 'bg-red-50 border-red-500',
  success: 'bg-green-50 border-green-500',
};
---

<div class={`p-4 rounded-lg border-l-4 ${styles[type]}`}>
  {title && <strong class="block mb-2">{title}</strong>}
  <slot />
</div>
```

## MDX Support

For more advanced content, you can enable MDX support:

```bash
npm install @astrojs/mdx
```

Then add it to your Astro config:

```js
import mdx from '@astrojs/mdx';

export default defineConfig({
  integrations: [tailwind(), mdx()],
});
```

## Adding Search

### Using Pagefind

Pagefind is a great option for static site search:

```bash
npm install pagefind
```

Add to your build script:

```json
{
  "scripts": {
    "build": "astro build && npx pagefind --source dist"
  }
}
```

## Performance Optimization

### Image Optimization

Use Astro's built-in image optimization:

```astro
---
import { Image } from 'astro:assets';
import myImage from '../assets/image.png';
---

<Image src={myImage} alt="Description" width={800} />
```

### Lazy Loading

Enable lazy loading for below-the-fold content:

```html
<img src="image.jpg" loading="lazy" alt="Description" />
```

## Analytics Integration

### Adding Plausible Analytics

```astro
<!-- In BaseLayout.astro head -->
<script
  defer
  data-domain="your-domain.com"
  src="https://plausible.io/js/script.js"
></script>
```

## Conclusion

These advanced techniques will help you build a professional, performant documentation site. Remember to test thoroughly before deploying to production!
