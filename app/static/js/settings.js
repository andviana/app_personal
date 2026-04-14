/**
 * Settings Module
 * Handles tab switching, backup/restore and CRUD modals.
 */

function switchTab(tabId) {
    document.querySelectorAll('.tab-content').forEach(tab => tab.classList.add('hidden'));
    const targetTab = document.getElementById('tab-' + tabId);
    if (targetTab) targetTab.classList.remove('hidden');

    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('bg-discord-400', 'text-primary-DEFAULT');
        btn.classList.add('text-text-muted', 'hover:bg-discord-400');
    });

    const activeBtn = document.getElementById('tab-btn-' + tabId);
    if (activeBtn) {
        activeBtn.classList.add('bg-discord-400', 'text-primary-DEFAULT');
        activeBtn.classList.remove('text-text-muted', 'hover:bg-discord-400');
    }

    localStorage.setItem('activeSettingsTab', tabId);
}

function openAddModal(entity) {
    const form = document.getElementById('modalForm');
    const title = document.getElementById('modalActionTitle');
    const input = document.getElementById('inputDenominacao');

    input.value = '';
    title.innerText = 'Novo ' + getEntityName(entity);
    form.action = '/settings/' + entity + '/add';

    document.getElementById('modalCrud').classList.remove('hidden');
    input.focus();
}

function openEditModal(entity, id, denominacao) {
    const form = document.getElementById('modalForm');
    const title = document.getElementById('modalActionTitle');
    const input = document.getElementById('inputDenominacao');

    input.value = denominacao;
    title.innerText = 'Editar ' + getEntityName(entity);
    form.action = '/settings/' + entity + '/edit/' + id;

    document.getElementById('modalCrud').classList.remove('hidden');
    input.focus();
}

function closeModal() {
    const modal = document.getElementById('modalCrud');
    if (modal) modal.classList.add('hidden');
}

function getEntityName(entity) {
    switch (entity) {
        case 'grupo_tarefa': return 'Grupo';
        case 'tipo_lista': return 'Categoria';
        case 'grupo_item': return 'Grupo de Item';
        default: return '';
    }
}

function handleRestore() {
    if (typeof Swal === 'undefined') {
        document.getElementById('backup_file').click();
        return;
    }

    Swal.fire({
        title: 'Atenção!',
        text: "A restauração irá APAGAR todos os dados atuais do aplicativo. Tem certeza que deseja continuar?",
        icon: 'warning',
        background: '#313338',
        color: '#dbdee1',
        confirmButtonColor: '#da373c',
        cancelButtonColor: '#4e5058',
        confirmButtonText: 'Sim, Restaurar!',
        cancelButtonText: 'Cancelar',
        customClass: {
            popup: 'rounded-[1.5rem]',
            title: 'text-text-heading font-black',
            confirmButton: 'rounded-xl px-6 py-2 font-bold uppercase tracking-widest text-xs',
            cancelButton: 'rounded-xl px-6 py-2 font-bold uppercase tracking-widest text-xs'
        }
    }).then((result) => {
        if (result.isConfirmed) {
            document.getElementById('backup_file').click();
        }
    });
}

async function processRestore(input, importUrl) {
    if (!input.files || input.files.length === 0) return;

    const file = input.files[0];
    const formData = new FormData();
    formData.append('backup_file', file);
    input.value = '';

    if (typeof Swal !== 'undefined') {
        Swal.fire({
            title: 'Restaurando...',
            text: 'Por favor, aguarde enquanto processamos os dados.',
            background: '#313338',
            color: '#dbdee1',
            allowOutsideClick: false,
            didOpen: () => {
                Swal.showLoading();
            },
            customClass: {
                popup: 'rounded-[1.5rem]'
            }
        });
    }

    try {
        const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') 
                         || document.querySelector('input[name="csrf_token"]')?.value;

        const response = await fetch(importUrl, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken
            },
            body: formData
        });

        const result = await response.json();

        if (result.success) {
            if (typeof Swal !== 'undefined') {
                Swal.fire({
                    title: 'Sucesso!',
                    text: result.message,
                    icon: 'success',
                    background: '#313338',
                    color: '#dbdee1',
                    confirmButtonColor: '#5865f2',
                    customClass: {
                        popup: 'rounded-[1.5rem]',
                        confirmButton: 'rounded-xl px-6 py-2 font-bold uppercase tracking-widest text-xs'
                    }
                }).then(() => {
                    window.location.reload();
                });
            } else {
                alert(result.message);
                window.location.reload();
            }
        } else {
            throw new Error(result.message);
        }
    } catch (error) {
        if (typeof Swal !== 'undefined') {
            Swal.fire({
                title: 'Erro!',
                text: error.message || 'Ocorreu um erro inesperado durante a restauração.',
                icon: 'error',
                background: '#313338',
                color: '#dbdee1',
                confirmButtonColor: '#5865f2',
                customClass: {
                    popup: 'rounded-[1.5rem]',
                    confirmButton: 'rounded-xl px-6 py-2 font-bold uppercase tracking-widest text-xs'
                }
            });
        } else {
            alert('Erro: ' + (error.message || 'Erro inesperado'));
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    // Retore active tab
    const activeTab = localStorage.getItem('activeSettingsTab') || 'conta';
    switchTab(activeTab);
});
// --- GLOBAL EXPOSURE ---
window.switchTab = switchTab;
window.openAddModal = openAddModal;
window.openEditModal = openEditModal;
window.closeModal = closeModal;
window.handleRestore = handleRestore;
window.processRestore = processRestore;
