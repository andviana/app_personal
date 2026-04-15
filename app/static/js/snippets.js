/**
 * Snippets Module
 * Handles AJAX loading, searching, and deletion.
 */

function confirmDelete(id, titulo, deleteUrl) {
    AppUI.confirmAction({
        title: 'Tem certeza?',
        text: `Deseja realmente remover o snippet "${titulo}"? Esta ação não pode ser desfeita.`,
        confirmText: 'Sim, remover!',
        onConfirm: () => {
            const form = document.getElementById('delete-form');
            if (form) {
                form.action = deleteUrl.replace('0', id);
                form.submit();
            }
        }
    });
}


function copyRawContent(content) {
    navigator.clipboard.writeText(content).then(() => {
        if (window.showToast) window.showToast('Conteúdo copiado!');
    });
}

function copySnippetUrl(url) {
    const finalUrl = url.includes('http') ? url : window.location.origin + url;
    navigator.clipboard.writeText(finalUrl).then(() => {
        if (typeof showToast !== 'undefined') showToast('Link copiado com sucesso!');
    });
}

function copySnippetLink(url) {
    const target = url || window.location.href;
    navigator.clipboard.writeText(target).then(() => {
        if (typeof showToast !== 'undefined') showToast('Link público copiado!');
    });
}

function toggleAccordion(id) {
    const content = document.getElementById('content-' + id);
    const icon = document.getElementById('icon-' + id);
    if (!content || !icon) return;
    
    const parent = content.closest('.mobile-snippet-item');
    
    if (content.classList.contains('hidden')) {
        content.classList.remove('hidden');
        icon.classList.add('rotate-180');
        parent.classList.add('ring-2', 'ring-primary-600', 'border-transparent');
    } else {
        content.classList.add('hidden');
        icon.classList.remove('rotate-180');
        parent.classList.remove('ring-2', 'ring-primary-600', 'border-transparent');
    }
}

function loadSnippet(id, element) {
    document.querySelectorAll('.snippet-list-item').forEach(el => el.classList.remove('active'));
    element.classList.add('active');

    const bodyContent = document.getElementById('detail-body');
    if (bodyContent) bodyContent.style.opacity = '0.5';

    fetch(`/snippets/${id}`, {
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        const emptyState = document.getElementById('empty-state');
        const snippetContent = document.getElementById('snippet-content');
        if (emptyState) emptyState.classList.add('hidden');
        if (snippetContent) snippetContent.classList.remove('hidden');
        
        document.getElementById('detail-title').textContent = data.titulo;
        document.getElementById('detail-desc').textContent = data.descricao || '';
        document.getElementById('detail-body').innerHTML = data.html;
        document.getElementById('detail-body').style.opacity = '1';
        
        // Update action buttons and data
        document.getElementById('detail-edit').href = `/snippets/editar/${data.id}`;
        document.getElementById('detail-link').href = `/snippets/${data.id}`;
        document.getElementById('detail-delete').setAttribute('data-id', data.id);
        document.getElementById('detail-delete').setAttribute('data-titulo', data.titulo);
        
        // Update share button
        const shareBtn = document.getElementById('detail-share');
        if (shareBtn) {
            shareBtn.onclick = () => copySnippetLink(data.share_url);
        }

        // Set raw content for copy button
        const copyBtn = document.getElementById('copy-content-btn');
        if (copyBtn) {
            copyBtn.setAttribute('data-id', data.id);
            copyBtn.setAttribute('data-raw', data.conteudo);
        }
        
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });
}


// Search logic with Debounce
document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('snippet-search');
    if (searchInput) {
        let searchTimeout;
        searchInput.addEventListener('input', (e) => {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                const q = e.target.value.toLowerCase();
                
                // Desktop filtering
                let desktopResults = 0;
                document.querySelectorAll('.snippet-list-item').forEach(item => {
                    const text = item.innerText.toLowerCase();
                    if (text.includes(q)) {
                        item.style.display = 'block';
                        desktopResults++;
                    } else {
                        item.style.display = 'none';
                    }
                });
                
                const emptyDesktop = document.getElementById('desktop-empty');
                if (emptyDesktop) emptyDesktop.style.display = desktopResults === 0 ? 'block' : 'none';

                // Mobile filtering
                document.querySelectorAll('.mobile-snippet-item').forEach(item => {
                    const text = item.innerText.toLowerCase();
                    if (text.includes(q)) {
                        item.style.display = 'block';
                    } else {
                        item.style.display = 'none';
                    }
                });
            }, 300);
        });
    }
});
// --- GLOBAL EXPOSURE ---
window.confirmDelete = confirmDelete;
window.copyRawContent = copyRawContent;
window.copySnippetUrl = copySnippetUrl;
window.copySnippetLink = copySnippetLink;
window.toggleAccordion = toggleAccordion;
window.loadSnippet = loadSnippet;
