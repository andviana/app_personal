/**
 * Pessoas Module
 * Handles index modals, clipboard and form dynamic rows/masks.
 */

// --- MODAL FUNCTIONS ---

function toggleModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.toggle('hidden');
        
        // Handle body scroll locking
        if (!modal.classList.contains('hidden')) {
            document.body.style.overflow = 'hidden';
        } else {
            // Check if there are other open modals before unlocking scroll
            const openModals = document.querySelectorAll('.fixed:not(.hidden)');
            if (openModals.length === 0) {
                document.body.style.overflow = '';
            }
        }
    }
}

// --- CLIPBOARD FUNCTIONS ---

function copyToClipboard(text, type = 'text', label = 'Item') {
    let contentToCopy = text;
    
    // Handle special types (extracting only numbers, etc)
    if (type === 'numbers') {
        contentToCopy = text.replace(/\D/g, '');
    } else if (type === 'date') {
        // Example: Convert DD/MM/YYYY to YYYY-MM-DD if needed, 
        // but usually we just copy as is. Keeping it flexible.
        contentToCopy = text;
    }

    navigator.clipboard.writeText(contentToCopy).then(() => {
        if (window.showToast) {
            window.showToast(`${label} copiado!`);
        } else {
            // Fallback to simple alert if showToast isn't available
            console.log(`${label} copiado: ${contentToCopy}`);
            const toast = document.createElement('div');
            toast.className = 'fixed bottom-4 right-4 bg-[#43b581] text-white px-6 py-3 rounded-xl shadow-2xl z-[200] animate-in fade-in slide-in-from-bottom-2';
            toast.innerText = `${label} copiado!`;
            document.body.appendChild(toast);
            setTimeout(() => toast.remove(), 2000);
        }
    }).catch(err => {
        console.error('Erro ao copiar: ', err);
    });
}

// --- FORM FUNCTIONS ---

function addRow(containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;

    const div = document.createElement('div');

    if (containerId === 'files-container') {
        div.className = 'grid grid-cols-1 md:grid-cols-2 gap-3 items-center animate-in fade-in slide-in-from-left-2 duration-300 bg-discord-300/30 p-3 rounded-2xl border border-discord-400';
        div.innerHTML = `
        <input type="text" name="arquivo_titulos[]" placeholder="Título do Documento"
               class="h-10 px-3 bg-[#1e1f22] border-none rounded-xl focus:ring-1 focus:ring-[#43b581] text-text-normal text-xs font-semibold">
        <div class="flex gap-2">
            <input type="text" name="arquivo_urls[]" placeholder="URL (Google Drive, OneDrive, etc)"
                   class="flex-1 h-10 px-3 bg-[#1e1f22] border-none rounded-xl focus:ring-1 focus:ring-[#43b581] text-text-normal text-xs font-semibold">
            <button type="button" onclick="this.closest('.grid').remove()" class="p-2 text-text-muted hover:text-danger hover:bg-danger/10 rounded-xl transition-all"><i class="ph-bold ph-trash"></i></button>
        </div>
    `;
    } else {
        div.className = 'flex gap-2 animate-in fade-in slide-in-from-left-2 duration-300';
        const name = containerId === 'addresses-container' ? 'enderecos[]' : 'telefones[]';
        const placeholder = containerId === 'addresses-container' ? 'Endereço completo...' : '(XX) XXXXX-XXXX';
        const mask = containerId === 'phones-container' ? 'oninput="maskPhone(this)" maxlength="15"' : '';

        div.innerHTML = `
        <input type="text" name="${name}" placeholder="${placeholder}" ${mask}
               class="flex-1 h-10 px-3 bg-[#1e1f22] border-none rounded-xl focus:ring-1 focus:ring-[#43b581] text-text-normal text-xs font-semibold">
        <button type="button" onclick="this.parentElement.remove()" class="p-2 text-text-muted hover:text-danger hover:bg-danger/10 rounded-xl transition-all"><i class="ph-bold ph-x"></i></button>
    `;
    }
    container.appendChild(div);
    div.querySelector('input').focus();
}

/**
 * Masks for inputs
 */
function maskCPF(i) {
    let v = i.value.replace(/\D/g, "");
    if (v.length <= 11) {
        v = v.replace(/(\d{3})(\d)/, "$1.$2");
        v = v.replace(/(\d{3})(\d)/, "$1.$2");
        v = v.replace(/(\d{3})(\d{1,2})$/, "$1-$2");
    }
    i.value = v;
}

function maskPIS(i) {
    let v = i.value.replace(/\D/g, "");
    if (v.length <= 11) {
        v = v.replace(/(\d{3})(\d)/, "$1.$2");
        v = v.replace(/(\d{5})(\d)/, "$1.$2");
        v = v.replace(/(\d{5}\.\d{2})(\d)/, "$1-$2");
    }
    i.value = v;
}

function maskPhone(i) {
    let v = i.value.replace(/\D/g, "");
    v = v.replace(/^(\d{2})(\d)/g, "($1) $2");
    v = v.replace(/(\d)(\d{4})$/, "$1-$2");
    i.value = v;
}

// --- ACTION FUNCTIONS ---

function confirmDelete(id, nome, deleteUrl) {
    if (typeof Swal === 'undefined') {
        if (confirm(`Tem certeza que deseja remover ${nome}?`)) {
            const form = document.getElementById('delete-form');
            form.action = deleteUrl.replace('0', id);
            form.submit();
        }
        return;
    }

    Swal.fire({
        title: 'Tem certeza?',
        text: `Deseja realmente remover "${nome}"? Esta ação não pode ser desfeita.`,
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#da373c',
        cancelButtonColor: '#4e5058',
        confirmButtonText: 'Sim, remover!',
        cancelButtonText: 'Cancelar',
        reverseButtons: true,
        customClass: {
            popup: 'discord-theme rounded-[2rem]',
            confirmButton: 'rounded-xl px-6 py-3 font-bold mb-2',
            cancelButton: 'rounded-xl px-6 py-3 font-bold mb-2'
        }
    }).then((result) => {
        if (result.isConfirmed) {
            const form = document.getElementById('delete-form');
            form.action = deleteUrl.replace('0', id);
            form.submit();
        }
    });
}

// --- GLOBAL EXPOSURE ---
// Attaching to window to ensure HTML onclick handlers work correctly

window.toggleModal = toggleModal;
window.copyToClipboard = copyToClipboard;
window.addRow = addRow;
window.maskCPF = maskCPF;
window.maskPIS = maskPIS;
window.maskPhone = maskPhone;
window.confirmDelete = confirmDelete;
