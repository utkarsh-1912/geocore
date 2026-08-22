/**
 * GeoCore Documentation Portal Interactive Engine
 * Author: Utkarsh Gupta
 * Copyright (c) 2026 GeoCore. All Rights Reserved.
 */

document.addEventListener('DOMContentLoaded', () => {
  // Copy Code Snippets
  const codeBlocks = document.querySelectorAll('pre code');
  codeBlocks.forEach(code => {
    const pre = code.parentElement;
    if (!pre.parentElement.classList.contains('code-wrapper')) {
      const wrapper = document.createElement('div');
      wrapper.className = 'relative group my-4';
      pre.parentNode.insertBefore(wrapper, pre);
      wrapper.appendChild(pre);

      const copyBtn = document.createElement('button');
      copyBtn.className = 'absolute top-3 right-3 px-2.5 py-1 text-xs rounded bg-surface border border-border text-text-muted hover:text-text-main opacity-90 sm:opacity-0 group-hover:opacity-100 transition-all flex items-center gap-1 shadow-sm touch-target';
      copyBtn.innerHTML = '<span>Copy</span>';

      copyBtn.addEventListener('click', async () => {
        try {
          await navigator.clipboard.writeText(code.innerText);
          copyBtn.innerHTML = '<span class="text-green-500 font-medium">Copied!</span>';
          setTimeout(() => {
            copyBtn.innerHTML = '<span>Copy</span>';
          }, 2000);
        } catch (e) {
          copyBtn.innerText = 'Failed';
        }
      });
      wrapper.appendChild(copyBtn);
    }
  });

  // Instant Documentation Search (Desktop & Mobile)
  const docsSearchInputs = document.querySelectorAll('#docs-search, #docs-search-mobile');
  const docNavLinks = document.querySelectorAll('.doc-nav-item');

  docsSearchInputs.forEach(input => {
    input.addEventListener('input', (e) => {
      const query = e.target.value.toLowerCase().trim();
      
      // Sync other search inputs if any
      docsSearchInputs.forEach(other => {
        if (other !== input) other.value = e.target.value;
      });

      docNavLinks.forEach(link => {
        const text = link.innerText.toLowerCase();
        const parentSection = link.closest('.doc-nav-section');
        if (!query || text.includes(query)) {
          link.style.display = 'flex';
        } else {
          link.style.display = 'none';
        }
      });

      // Filter section headings visibility
      document.querySelectorAll('.doc-nav-section').forEach(sec => {
        const visibleLinks = sec.querySelectorAll('.doc-nav-item[style="display: flex;"], .doc-nav-item:not([style*="display: none"])');
        if (query && visibleLinks.length === 0) {
          sec.style.display = 'none';
        } else {
          sec.style.display = 'block';
        }
      });
    });
  });

  // Mobile Docs Sidebar Drawer & Backdrop
  const toggleDocsSidebar = document.getElementById('toggle-docs-sidebar');
  const closeDocsSidebar = document.getElementById('close-docs-sidebar');
  const docsSidebar = document.getElementById('docs-sidebar');
  const docsBackdrop = document.getElementById('docs-backdrop');

  function openSidebar() {
    if (docsSidebar && docsBackdrop) {
      docsSidebar.classList.remove('-translate-x-full');
      docsBackdrop.classList.remove('hidden');
      document.body.style.overflow = 'hidden';
      if (window.lucide) window.lucide.createIcons();
    }
  }

  function closeSidebar() {
    if (docsSidebar && docsBackdrop) {
      docsSidebar.classList.add('-translate-x-full');
      docsBackdrop.classList.add('hidden');
      document.body.style.overflow = '';
    }
  }

  if (toggleDocsSidebar) toggleDocsSidebar.addEventListener('click', openSidebar);
  if (closeDocsSidebar) closeDocsSidebar.addEventListener('click', closeSidebar);
  if (docsBackdrop) docsBackdrop.addEventListener('click', closeSidebar);

  // Close sidebar on clicking any navigation link
  docNavLinks.forEach(link => {
    link.addEventListener('click', () => {
      if (window.innerWidth < 1024) {
        closeSidebar();
      }
    });
  });

  // ScrollSpy for Active Table of Contents
  const observerOptions = {
    root: null,
    rootMargin: '-20% 0px -70% 0px',
    threshold: 0
  };

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const id = entry.target.getAttribute('id');
        if (id) {
          document.querySelectorAll('.toc-link').forEach(link => {
            if (link.getAttribute('href') === `#${id}`) {
              link.classList.add('text-primary', 'font-semibold', 'border-l-2', 'border-primary', 'pl-2');
              link.classList.remove('text-text-muted');
            } else {
              link.classList.remove('text-primary', 'font-semibold', 'border-l-2', 'border-primary', 'pl-2');
              link.classList.add('text-text-muted');
            }
          });
        }
      }
    });
  }, observerOptions);

  document.querySelectorAll('section[id], h2[id], h3[id]').forEach(elem => {
    observer.observe(elem);
  });
});
