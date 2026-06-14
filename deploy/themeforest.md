# ThemeForest Item Upload Form: VResume

## Name & Description
**Name:** VResume - Personal Portfolio & Resume Django CMS

**Key Features:**
1. Built with Django 5 & Wagtail 6 CMS
2. Dynamic HTMX & Tailwind CSS v4 Frontend
3. Fully Responsive & SEO Optimized Design
4. Modular Docker Infrastructure for Deployment
5. Integrated Newsletter & Contact Form Systems

**HTML Description:**
```html
<h3>VResume - The Ultimate Personal Portfolio CMS</h3>
<p>VResume is a modern, self-hosted portfolio and resume management system designed for professionals who want full control over their online presence. Built with <strong>Django 5</strong>, <strong>Wagtail 6</strong>, <strong>HTMX</strong>, and <strong>Tailwind CSS v4</strong>, it combines high performance with an intuitive editing experience.</p>

<h4>Key Features</h4>
<ul>
    <li><strong>Professional CMS:</strong> Powered by Wagtail, offering a clean and powerful interface for managing all your content.</li>
    <li><strong>HTMX Magic:</strong> Experience lightning-fast, dynamic page updates without the overhead of heavy SPA frameworks.</li>
    <li><strong>Tailwind CSS v4:</strong> Utilizing the latest in CSS technology for a sleek, modern, and highly customizable design.</li>
    <li><strong>Comprehensive Sections:</strong> Includes Home, About, Resume (Timeline), Portfolio (Filterable), and a Full-featured Blog.</li>
    <li><strong>Modular Docker:</strong> Ready for production with a robust, modular Docker Compose architecture.</li>
    <li><strong>SEO & Accessibility:</strong> Optimized for search engines and built with accessibility best practices in mind.</li>
    <li><strong>Newsletter & Contact:</strong> Integrated forms with background task processing (Celery/Redis).</li>
</ul>

<h4>What's Included?</h4>
<ul>
    <li>Full Django Source Code</li>
    <li>Wagtail CMS Integration</li>
    <li>Webpack Asset Pipeline</li>
    <li>Docker & Docker Compose Configurations</li>
    <li>Comprehensive Documentation</li>
    <li>Initial Data Seeding Scripts</li>
</ul>
```

## Category & Attributes
*   **Category:** CMS / Site Templates
*   **High Resolution:** Yes
*   **Compatible Browsers:** IE11, Firefox, Safari, Opera, Chrome, Edge
*   **Compatible With:** Bootstrap 5.x, Tailwind CSS, Django 5.x, Wagtail 6.x
*   **ThemeForest Files Included:** Python Files, HTML Files, CSS Files, JS Files, SCSS Files, PHP Files (N/A but often checked for CMS), PSD (N/A)
*   **Columns:** 1
*   **Layout:** Responsive

## Tags
portfolio, resume, cv, django, wagtail, cms, htmx, tailwind, responsive, personal, developer, creative, blog, docker, seo

## Pricing
*   **Regular License:** $19
*   **Extended License:** $750

---

## 📝 Archive Notes & Instructions

To prepare the final "Main File" for ThemeForest upload, use the following command. This command creates a compressed archive of the project while strictly excluding files defined in `.gitignore` and `.dockerignore`, as well as version control data.

### 📦 Archive Command

Run this command from the project root:

```bash
tar -czvf VResume_Main_File.tar.gz \
    --exclude-vcs \
    --exclude-from=.gitignore \
    --exclude-from=.dockerignore \
    .
```

**Note:** If you want to include this `themeforest.md` file in the archive for reference, remove the `--exclude="themeforest.md"` line.

### 🔍 Verification
After running the command, you can verify the contents of the archive with:
```bash
tar -tf VResume_Main_File.tar.gz
```

### 🚀 Upload Checklist
1. **Thumbnail:** JPEG or PNG (80x80px)
2. **Theme Preview:** ZIP file of images (590x300px main preview + others)
3. **Main File:** The `VResume_Main_File.tar.gz` generated above.
4. **Documentation:** Ensure the `docs/` folder is included in the Main File.
