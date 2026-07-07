# Jaya Arun Kumar Tulluri - Personal Portfolio

A sleek, animated, and minimalist personal portfolio leveraging modern web design principles like Neo-Brutalism, Glassmorphism, and Neumorphism. This portfolio showcases professional experience, core competencies, and personal projects in a highly performant, single-file HTML architecture.

## Architecture

This project originally started as an Astro + Tailwind documentation site but has been refactored entirely into a **single, dependency-free HTML file (`index.html`)** for maximum portability, simplicity, and performance. 

- **Zero-Build Pipeline:** No Node.js build steps or complex bundlers required for production.
- **Embedded CSS & Scripts:** All Tailwind directives, custom CSS (glassmorphism/neumorphism), light/dark theme switching, and lightweight scroll animations are contained directly within the file.
- **Offline Capable:** Drop the file into any browser and it works immediately *(Note: The "My current activities" modal uses `fetch()` and requires a local or live server to bypass CORS)*.

## Design Highlights

- **Interactive Markdown Dialog:** Fetches and parses `MyCurrentActivities.md` into a native `<dialog>` modal using `marked.js` keeping HTML clean.

- **Glassmorphism:** Elegant frosted glass layers (`.glass-card`, `.glass-nav`) with subtle ambient blur over an animated, deep-space gradient background.
- **Neumorphism:** Tactical use of inset and drop shadows (`.neu-tag`) for skill pills, complementing the dark aesthetic.
- **Responsive Layout:** A fixed navigation bar on desktop that transitions to a sleek, glassmorphism off-canvas menu for mobile viewing.
- **Micro-interactions:** Custom hover effects, CSS keyframe gradient text animations, and automated scroll reveal states (`IntersectionObserver`).

## Tech Stack

- **HTML5:** Semantic architecture
- **CSS3 / Tailwind CSS (CDN):** Core styling engine with custom variants
- **JavaScript (Vanilla):** Scroll observers and mobile menu toggles

## Getting Started

Because the project has been simplified to its purest form, there are no dependencies to install.

### Running Locally

**Method 1: Direct File Access**
Double-click `index.html` to open it in any modern browser.

**Method 2: Live Server (Recommended for development)**
If you are using VS Code, use the [Live Server](https://marketplace.visualstudio.com/items?itemName=ritwickdey.LiveServer) extension to serve the file and get hot-reloading on save.

**Method 3: npm serve**
If you have Node installed, you can still use:
```bash
npm install -g serve
serve .
```

### Deployment

Because the project relies on the browser's `fetch()` API for the activities modal, the site must be served over HTTP/HTTPS rather than a local file path (`file://`). To make the site available live, you can deploy it instantly for free to any of the following platforms. Since there is no `package.json` build step, you don't even need a build command.

#### Deploying to Vercel (Recommended)
1. Push this project folder to a GitHub repository.
2. Log into [Vercel](https://vercel.com/) and click **Add New → Project**.
3. Import your GitHub repository.
4. Under "Framework Preset", select **Other**.
5. Leave the "Build Command" and "Output Directory" completely blank (or default).
6. Click **Deploy**. Vercel will instantly serve your `index.html` file.

#### Deploying to Netlify
1. Log into [Netlify](https://app.netlify.com/).
2. You can either:
   - **Link to GitHub:** Go to "Add new site" → "Import an existing project" → Select your repo. Leave build commands blank.
   - **Drag and Drop:** Go to [Netlify Drop](https://app.netlify.com/drop) and just drag your local portfolio folder over into the browser. It will deploy your site in seconds.

#### Deploying to GitHub Pages
1. Push this project folder to a new repository on GitHub (e.g., `portfolio`).
2. Go to your repository **Settings** tab.
3. On the left sidebar, click **Pages**.
4. Under "Build and deployment", select **Deploy from a branch**.
5. Choose your `main` (or `master`) branch, and set the folder to `/ (root)`.
6. Click **Save**. Within a minute, your link will be live at `https://<your-username>.github.io/<repo-name>`.

## Customization

To edit the portfolio, simply open `index.html`. 
- **Personal Details:** Search for standard IDs like `#hero`, `#about`, `#experience` to modify text.
- **Styling:** Top `<style>` block contains all custom CSS classes and animations.

## Author

**Jaya Arun Kumar Tulluri**
- **Role**: Senior Systems Engineer
- **Email**: jayaarunkumartulluri2@gmail.com
- **LinkedIn**: [Jaya Arun Kumar Tulluri](https://linkedin.com/in/jayaarunkumar-tulluri)
