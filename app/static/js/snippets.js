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
        parent.classList.add('ring-2', 'ring-primary', 'border-transparent');
    } else {
        content.classList.add('hidden');
        icon.classList.remove('rotate-180');
        parent.classList.remove('ring-2', 'ring-primary', 'border-transparent');
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
        
        // Update tags in detail
        const tagsContainer = document.getElementById('detail-tags');
        if (tagsContainer) {
            tagsContainer.innerHTML = data.tags.map(t => `
                <span class="px-3 py-1 rounded-full text-[10px] font-black tracking-wider uppercase text-white shadow-sm" style="background-color: ${t.cor}">
                    ${t.denominacao}
                </span>
            `).join('');
        }
        
        // Update action buttons and data
        document.getElementById('detail-edit').href = `/snippets/editar/${data.id}`;
        document.getElementById('detail-link').href = `/snippets/${data.id}`;
        document.getElementById('detail-delete').setAttribute('data-id', data.id);
        document.getElementById('detail-delete').setAttribute('data-titulo', data.titulo);
        document.getElementById('detail-tags-btn').setAttribute('data-id', data.id);
        
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

// --- Tag Management ---

function openManageTagsModal() {
    document.getElementById('modal-manage-tags').classList.remove('hidden');
    loadTagsList();
    // Establish focus on the tag name input
    const tagInput = document.querySelector('#form-add-tag input[name="denominacao"]');
    if (tagInput) {
        setTimeout(() => tagInput.focus(), 100);
    }
}

function closeManageTagsModal() {
    document.getElementById('modal-manage-tags').classList.add('hidden');
}

function loadTagsList() {
    fetch('/snippets/tags/list')
        .then(res => res.json())
        .then(tags => {
            const container = document.getElementById('tags-list-container');
            if (tags.length === 0) {
                container.innerHTML = '<p class="text-center py-4 text-text-muted text-xs italic">Nenhuma tag cadastrada.</p>';
                return;
            }
            container.innerHTML = tags.map(t => `
                <div class="flex justify-between items-center bg-background p-3 rounded-xl border border-slate-200">
                    <div class="flex items-center gap-3">
                        <div class="w-4 h-4 rounded-full" style="background-color: ${t.cor}"></div>
                        <span class="text-sm font-bold text-text-heading">${t.denominacao}</span>
                    </div>
                    <button onclick="deleteTag(${t.id}, '${t.denominacao}')" class="p-3 md:p-2 -m-1 md:m-0 text-text-muted hover:text-danger hover:scale-110 transition-all">
                        <i class="ph-bold ph-trash text-lg"></i>
                    </button>
                </div>
            `).join('');
        });
}

function deleteTag(id, name) {
    AppUI.confirmAction({
        title: 'Excluir Tag?',
        text: `Deseja realmente excluir a tag "${name}"? Ela será removida de todos os snippets associados.`,
        confirmText: 'Sim, excluir!',
        onConfirm: () => {
            const formData = new FormData();
            formData.append('csrf_token', document.querySelector('input[name="csrf_token"]').value);

            fetch(`/snippets/tags/delete/${id}`, {
                method: 'POST',
                body: formData,
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    loadTagsList();
                    if (window.showToast) window.showToast('Tag removida!');
                }
            });
        }
    });
}

let currentSnippetId = null;

function openSnippetTagsModal(snippetId) {
    currentSnippetId = snippetId;
    document.getElementById('modal-snippet-tags').classList.remove('hidden');
    
    // Pegar tags do snippet atual (verificando se o painel está carregado)
    fetch(`/snippets/${snippetId}`, { headers: {'X-Requested-With': 'XMLHttpRequest'} })
        .then(res => res.json())
        .then(data => {
            const activeTagIds = data.tags.map(t => t.id);
            document.getElementById('snippet-tags-title').textContent = data.titulo;
            
            // Carregar todas as tags disponíveis
            fetch('/snippets/tags/list')
                .then(res => res.json())
                .then(allTags => {
                    const container = document.getElementById('snippet-tags-selection');
                    if (allTags.length === 0) {
                        container.innerHTML = '<p class="text-center py-4 text-text-muted text-xs italic">Crie tags primeiro em "Gerenciar Tags".</p>';
                        return;
                    }
                    container.innerHTML = allTags.map(t => `
                        <label class="flex items-center justify-between bg-surface p-4 rounded-xl border border-slate-200 cursor-pointer hover:bg-surface-hover transition-colors">
                            <div class="flex items-center gap-3">
                                <div class="w-3 h-3 rounded-full" style="background-color: ${t.cor}"></div>
                                <span class="text-sm font-bold text-text-heading">${t.denominacao}</span>
                            </div>
                            <input type="checkbox" onchange="toggleSnippetTag(this, ${t.id})" 
                                ${activeTagIds.includes(t.id) ? 'checked' : ''}
                                class="w-5 h-5 rounded border-slate-300 bg-surface-sunken text-primary focus:ring-primary">
                        </label>
                    `).join('');
                });
        });
}

function closeSnippetTagsModal() {
    document.getElementById('modal-snippet-tags').classList.add('hidden');
    // Em vez de recarregar a página, atualizamos apenas o snippet atual
    if (currentSnippetId) {
        refreshSnippetUI(currentSnippetId);
    }
}

function refreshSnippetUI(snippetId) {
    fetch(`/snippets/${snippetId}`, { headers: {'X-Requested-With': 'XMLHttpRequest'} })
        .then(res => res.json())
        .then(data => {
            // 1. Atualizar Detail tags
            const tagsContainer = document.getElementById('detail-tags');
            if (tagsContainer) {
                tagsContainer.innerHTML = data.tags.map(t => `
                    <span class="px-3 py-1 rounded-full text-[10px] font-black tracking-wider uppercase text-white shadow-sm" style="background-color: ${t.cor}">
                        ${t.denominacao}
                    </span>
                `).join('');
            }

            // 2. Atualizar Desktop List tags
            const desktopItem = document.querySelector(`.snippet-list-item[data-id="${snippetId}"] .flex.flex-wrap`);
            if (desktopItem) {
                desktopItem.innerHTML = data.tags.map(t => `
                    <span class="px-2 py-0.5 rounded-full text-[9px] font-black tracking-wider uppercase text-white shadow-sm" style="background-color: ${t.cor}">
                        ${t.denominacao}
                    </span>
                `).join('');
            }

            // 3. Atualizar Mobile List tags
            const mobileItem = document.querySelector(`.mobile-snippet-item button[data-id="${snippetId}"] .flex.flex-wrap`);
            if (mobileItem) {
                mobileItem.innerHTML = data.tags.map(t => `
                    <span class="px-2 py-0.5 rounded-full text-[8px] font-black tracking-wider uppercase text-white shadow-sm" style="background-color: ${t.cor}">
                        ${t.denominacao}
                    </span>
                `).join('');
            }
        });
}

function toggleSnippetTag(checkbox, tagId) {
    const formData = new FormData();
    formData.append('tag_id', tagId);
    formData.append('csrf_token', document.querySelector('input[name="csrf_token"]').value);

    fetch(`/snippets/${currentSnippetId}/tags/toggle`, {
        method: 'POST',
        body: formData
    })
    .then(res => res.json())
    .then(data => {
        if (!data.success) {
            checkbox.checked = !checkbox.checked;
            if (window.showToast) window.showToast('Erro ao atualizar tags', 'error');
        } else {
            // Feedback visual imediato opcional? O reload já foi removido.
        }
    });
}

// Search logic with Debounce
document.addEventListener('DOMContentLoaded', () => {
    // Handler para Criação de Tag via AJAX
    const tagForm = document.getElementById('form-add-tag');
    if (tagForm) {
        tagForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const formData = new FormData(tagForm);
            
            fetch('/snippets/tags/add', {
                method: 'POST',
                body: formData,
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    loadTagsList();
                    const nameInput = tagForm.querySelector('input[name="denominacao"]');
                    nameInput.value = '';
                    nameInput.focus(); // Return focus after save
                    if (window.showToast) window.showToast(`Tag ${data.tag.denominacao} criada!`);
                }
            });
        });
    }

    const searchInput = document.getElementById('snippet-search');
    if (searchInput) {
        let searchTimeout;
        searchInput.addEventListener('input', (e) => {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                const q = e.target.value.toLowerCase().trim();
                
                // Desktop filtering
                let desktopResults = 0;
                document.querySelectorAll('.snippet-list-item').forEach(item => {
                    const text = item.innerText.toLowerCase();
                    const match = q.startsWith('#') 
                        ? text.includes(q.substring(1)) // Se for #TAG, procura o nome da tag
                        : text.includes(q);
                        
                    if (match) {
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
                    const match = q.startsWith('#') 
                        ? text.includes(q.substring(1))
                        : text.includes(q);
                        
                    if (match) {
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
window.openManageTagsModal = openManageTagsModal;
window.closeManageTagsModal = closeManageTagsModal;
window.openSnippetTagsModal = openSnippetTagsModal;
window.closeSnippetTagsModal = closeSnippetTagsModal;
window.deleteTag = deleteTag;
window.toggleSnippetTag = toggleSnippetTag;
