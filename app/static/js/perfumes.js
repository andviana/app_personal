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
    if (fieldNome) fieldNome.focus();
}

function closeModal() {
    const modal = document.getElementById('modalPerfume');
    if (modal) modal.classList.add('hidden');
}

function updateImagePreview(url) {
    const previewArea = document.getElementById('formImgPreview');
    const previewImg = document.getElementById('previewImg');
    
    if (!previewArea || !previewImg) return;

    if (url && (url.match(/\.(jpeg|jpg|gif|png|webp|avif)$/) != null)) {
        previewImg.src = url;
        previewArea.classList.remove('hidden');
    } else {
        previewArea.classList.add('hidden');
    }
}

function confirmDeleteByForm(action, nome) {
    if (typeof Swal === 'undefined') {
        if (confirm(`Deseja realmente excluir "${nome}"? Esta ação não pode ser desfeita.`)) {
            const form = document.getElementById('deletePerfumeForm');
            form.action = action;
            form.submit();
        }
        return;
    }

    Swal.fire({
        title: 'Remover Perfume?',
        text: `Deseja realmente excluir "${nome}"? Esta ação não pode ser desfeita.`,
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#da373c',
        cancelButtonColor: '#383a40',
        confirmButtonText: 'Sim, excluir!',
        cancelButtonText: 'Cancelar',
        reverseButtons: true,
        customClass: {
            popup: 'rounded-[1.5rem] bg-discord-200 text-text-normal',
            title: 'text-text-heading font-black',
            content: 'text-text-muted',
            confirmButton: 'rounded-xl px-6 py-2.5 font-bold uppercase tracking-widest text-xs',
            cancelButton: 'rounded-xl px-6 py-2.5 font-bold uppercase tracking-widest text-xs'
        }
    }).then((result) => {
        if (result.isConfirmed) {
            const form = document.getElementById('deletePerfumeForm');
            form.action = action;
            form.submit();
        }
    });
}
