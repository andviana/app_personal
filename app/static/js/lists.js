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
    const modal = document.getElementById('modalImportarURL');
    if (!modal) return;
    modal.classList.remove('hidden');
    const input = document.getElementById('urlInputScrape');
    if (input) input.focus();
}

function closeScrapeModal() {
    const modal = document.getElementById('modalImportarURL');
    if (!modal) return;
    modal.classList.add('hidden');
}

function openViewItemModal(btn) {
    const modal = document.getElementById('modalVerItem');
    if (!modal) return;
    const content = modal.querySelector('.bg-surface');

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

