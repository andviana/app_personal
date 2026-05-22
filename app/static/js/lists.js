/**
 * Lists Module
 * Handles list item modals, scrapers and toggles.
 */

function openEditItemModal(btn) {
    const id = btn.getAttribute('data-id');
    const nome = btn.getAttribute('data-nome');
    const grupoId = btn.getAttribute('data-grupo');
    const valor = btn.getAttribute('data-valor');
    const link = btn.getAttribute('data-link');

    document.getElementById('edit_item_nome').value = nome;
    document.getElementById('edit_item_grupo').value = grupoId;
    document.getElementById('edit_item_valor').value = (valor && valor !== 'None') ? valor : '';
    document.getElementById('edit_item_link').value = (link && link !== 'None') ? link : '';
    document.getElementById('formEditarItem').action = '/lists/item/' + id + '/edit';
    document.getElementById('modalEditarItem').classList.remove('hidden');
}

function openScrapeModal() {
    console.log('[Lists] Opening Scrape Modal...');
    const modal = document.getElementById('modalImportarURL');
    if (!modal) {
        console.error('[Lists] Error: Modal element "modalImportarURL" not found!');
        return;
    }
    
    const content = modal.querySelector('.modal-content');
    
    // Explicitly show the modal container
    modal.classList.remove('hidden');
    modal.style.display = 'flex'; // Ensure flex display
    
    if (content) {
        console.log('[Lists] Animating modal content...');
        setTimeout(() => {
            content.classList.remove('scale-95', 'opacity-0');
            content.classList.add('scale-100', 'opacity-100');
        }, 30);
    } else {
        console.warn('[Lists] Warning: ".modal-content" not found, showing modal without transition.');
    }
    
    const input = document.getElementById('urlInputScrape');
    if (input) input.focus();
}

function closeScrapeModal() {
    const modal = document.getElementById('modalImportarURL');
    if (!modal) return;
    const content = modal.querySelector('.modal-content');
    if (content) {
        content.classList.add('scale-95', 'opacity-0');
        content.classList.remove('scale-100', 'opacity-100');
    }
    setTimeout(() => {
        modal.classList.add('hidden');
        modal.style.display = ''; // Clear explicit flex
    }, 300);
}

function openViewItemModal(btn) {
    const modal = document.getElementById('modalVerItem');
    if (!modal) return;
    const content = modal.querySelector('.bg-discord-200');

    const id = btn.getAttribute('data-id');
    const nome = btn.getAttribute('data-nome').toUpperCase();
    const grupo = btn.getAttribute('data-grupo').toUpperCase();
    const valor = btn.getAttribute('data-valor');
    const link = btn.getAttribute('data-link');

    document.getElementById('view_item_nome').innerText = nome;
    document.getElementById('view_item_grupo').innerText = grupo;

    if (valor) {
        document.getElementById('view_item_valor').innerText = parseFloat(valor).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
    } else {
        document.getElementById('view_item_valor').innerText = '--';
    }

    const linkContainer = document.getElementById('view_item_link_container');
    const linkElem = document.getElementById('view_item_link');
    const linkText = document.getElementById('view_item_link_text');

    if (link && link !== '' && link !== 'None') {
        linkContainer.classList.remove('hidden');
        linkElem.href = link;
        linkText.innerText = link;
    } else {
        linkContainer.classList.add('hidden');
    }

    // Configure Edit/Delete buttons in the Modal
    const btnEdit = document.getElementById('btnEditFromView');
    btnEdit.setAttribute('data-id', id);
    btnEdit.setAttribute('data-nome', btn.getAttribute('data-nome'));
    btnEdit.setAttribute('data-grupo', btn.getAttribute('data-grupo-id') || '');
    btnEdit.setAttribute('data-valor', valor);
    btnEdit.setAttribute('data-link', link);

    document.getElementById('formDeleteFromView').action = '/lists/item/' + id + '/delete';

    modal.classList.remove('hidden');
    content.classList.remove('animate-in', 'zoom-in-95');
    void content.offsetWidth;
    content.classList.add('animate-in', 'zoom-in-95');
}

document.addEventListener('DOMContentLoaded', () => {
    const formScrape = document.getElementById('formScrape');
    if (formScrape) {
        formScrape.addEventListener('submit', function (e) {
            const btn = document.getElementById('btnScrapeSubmit');
            const txt = document.getElementById('txtScrapeBtn');
            const loader = document.getElementById('loaderScrape');
            const icon = document.getElementById('iconScrapeBtn');

            btn.disabled = true;
            btn.classList.add('opacity-80', 'cursor-not-allowed');
            txt.innerText = 'EXTRAINDO DADOS...';
            loader.classList.remove('hidden');
            icon.classList.add('hidden');
        });
    }
});

function confirmDelete(event, form, itemName = 'este item') {
    event.preventDefault();
    AppUI.confirmAction({
        title: 'Remover item?',
        text: `Deseja realmente remover "${itemName}"? Essa ação não pode ser desfeita!`,
        confirmText: 'Sim, excluir',
        onConfirm: () => {
            if (window.saveScrollPosition) window.saveScrollPosition();
            form.submit();
        }
    });
}

