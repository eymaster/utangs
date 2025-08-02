document.querySelector('#themeToggle').addEventListener('click', () => {
    const html = document.documentElement;
    const isDark = html.getAttribute('data-bs-theme') === 'dark';
    html.setAttribute('data-bs-theme', isDark ? 'light' : 'dark');
    localStorage.setItem('theme', isDark ? 'light' : 'dark');
});

document.addEventListener('DOMContentLoaded', () => {
    const stored = localStorage.getItem('theme');
    if (stored) {
        document.documentElement.setAttribute('data-bs-theme', stored);
    }
});
