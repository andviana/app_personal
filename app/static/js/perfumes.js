/**
 * Perfumes Module
 * Handles perfume filtering, image preview and CRUD modals.
 */

function filterPerfumes() {
    const searchInput = document.getElementById('searchPerfume');
    if (!searchInput) return;

    const query = searchInput.value.toLowerCase();
    const cards = document.querySelectorAll('.perfume-card');
    
    cards.forEach(card => {
        const nome = card.getAttribute('data-nome');
        const corr = card.getAttribute('data-correspondente');
        if (nome.includes(query) || corr.includes(query)) {
            card.style.display = 'flex';
        } else {
            card.style.display = 'none';
        }
    });
}

function openPerfumeModal(btn) {
    const id = btn.dataset.id;
    const nome = btn.dataset.nome;
    const marca = btn.dataset.marca;
    const corr = btn.dataset.correspondente;
    const valor = btn.dataset.valor;
    const url = btn.dataset.url;
    const url_imagem = btn.dataset.url_imagem;
    
    openModal('edit', id, nome, marca, corr, valor, url, url_imagem);
}

function openModal(mode, id = '', nome = '', marca = '', corr = '', valor = '', url = '', url_imagem = '') {
    const modal = document.getElementById('modalPerfume');
    const form = document.getElementById('perfumeForm');
    const title = document.getElementById('modalTitle');
    
    if (!modal || !form || !title) return;

    title.innerText = mode === 'add' ? 'Novo Perfume' : 'Editar Perfume';
    form.action = mode === 'add' ? "/perfumes/add" : `/perfumes/edit/${id}`;
    
    const fieldNome = document.getElementById('field-nome');
    const fieldMarca = document.getElementById('field-marca');
    const fieldCorr = document.getElementById('field-correspondente');
    const fieldValor = document.getElementById('field-valor');
    const fieldUrl = document.getElementById('field-url');
    const fieldUrlImg = document.getElementById('field-url-imagem');

    if (fieldNome) fieldNome.value = nome;
    if (fieldMarca) fieldMarca.value = marca;
    if (fieldCorr) fieldCorr.value = corr;
    if (fieldValor) fieldValor.value = valor;
    if (fieldUrl) fieldUrl.value = url;
    if (fieldUrlImg) fieldUrlImg.value = url_imagem;
    
    updateImagePreview(url_imagem || url);
    
    modal.classList.remove('hidden');
    modal.classList.add('flex');
    if (fieldNome) {
        setTimeout(() => fieldNome.focus(), 50);
    }
}

function closeModal() {
    const modal = document.getElementById('modalPerfume');
    if (modal) {
        modal.classList.add('hidden');
        modal.classList.remove('flex');
    }
}

function updateImagePreview(url) {
    const previewArea = document.getElementById('formImgPreview');
    const previewImg = document.getElementById('previewImg');
    
    if (!previewArea || !previewImg) return;

    if (url && (url.startsWith('http://') || url.startsWith('https://') || url.startsWith('/'))) {
        previewImg.onload = () => {
            previewArea.classList.remove('hidden');
        };
        previewImg.onerror = () => {
            previewArea.classList.add('hidden');
        };
        previewImg.src = url;
    } else {
        previewArea.classList.add('hidden');
        previewImg.src = '';
    }
}

function confirmDeleteByForm(action, nome) {
    AppUI.confirmAction({
        title: 'REMOVER PERFUME',
        text: `Deseja realmente excluir "${nome}"? Esta ação não pode ser desfeita.`,
        confirmText: 'SIM, EXCLUIR',
        onConfirm: () => {
            const form = document.getElementById('deletePerfumeForm');
            form.action = action;
            form.submit();
        }
    });
}
