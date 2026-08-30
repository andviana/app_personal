/**
 * Tasks Module
 * Handles task filtering, group toggling and CRUD modals.
 */
function togglePanel() {
    const filterBar = document.getElementById('filterBar');
    const taskForm = document.getElementById('taskFormArea');
    const toggleBtn = document.getElementById('toggleModeBtn');

    if (!filterBar || !taskForm || !toggleBtn) return;

    if (filterBar.classList.contains('hidden')) {
        filterBar.classList.remove('hidden');
        taskForm.classList.add('hidden');
        toggleBtn.innerHTML = '<i class="ph-bold ph-plus text-lg"></i>';
        toggleBtn.classList.add('!bg-primary-light', '!text-primary', '!border-primary/30');
    } else {
        filterBar.classList.add('hidden');
        taskForm.classList.remove('hidden');
        toggleBtn.innerHTML = '<i class="ph-bold ph-magnifying-glass text-lg"></i> <span class="hidden md:inline">Pesquisar</span>';
        toggleBtn.classList.remove('!bg-primary-light', '!text-primary', '!border-primary/30');
    }
}

function openEditModal(id, descricao, grupo_id, status) {
    const descInput = document.getElementById('editDescricao');
    const grupoInput = document.getElementById('editGrupoId');
    const statusInput = document.getElementById('editStatusNome');
    const form = document.getElementById('formEditTarefa');

    if (descInput) descInput.value = descricao;
    if (grupoInput) grupoInput.value = grupo_id;
    if (statusInput) statusInput.value = status;
    if (form) form.action = "/tasks/edit/" + id;

    AppUI.toggleModal('modalEditTarefa', true);
}

function openAddTaskModal(grupoId, grupoDenominacao) {
    const titleSub = document.getElementById('modalNovaTarefaGrupo');
    const hiddenInput = document.getElementById('novaTarefaGrupoId');
    const descInput = document.getElementById('novaTarefaDescricao');

    if (titleSub) titleSub.textContent = "Grupo: " + grupoDenominacao.toUpperCase();
    if (hiddenInput) hiddenInput.value = grupoId;
    if (descInput) descInput.value = "";

    AppUI.toggleModal('modalNovaTarefa', true);

    setTimeout(() => {
        if (descInput) descInput.focus();
    }, 100);
}

function confirmDeleteTask(id, descricao) {
    AppUI.confirmAction({
        title: 'Excluir Tarefa?',
        text: `Deseja realmente remover a tarefa "${descricao}"?`,
        confirmText: 'Sim, excluir!',
        onConfirm: async () => {
            const form = document.getElementById('delete-task-form');
            const url = "/tasks/delete/" + id;
            try {
                const response = await fetch(url, {
                    method: 'POST',
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest'
                    },
                    body: new FormData(form)
                });
                const data = await response.json();
                if (data.success) {
                    const btn = document.querySelector(`.task-row button[data-id="${id}"]`);
                    if (btn) {
                        const row = btn.closest('.task-row');
                        const groupContainer = row.closest('.task-group');
                        row.remove();
                        if (groupContainer && groupContainer.querySelectorAll('.task-row').length === 0) {
                            groupContainer.remove();
                        }
                    }
                    if (window.AppUI && window.AppUI.toast) {
                        window.AppUI.toast('success', 'Tarefa excluída com sucesso.');
                    }
                }
            } catch (err) {
                console.error(err);
                if (window.AppUI && window.AppUI.toast) {
                    window.AppUI.toast('error', 'Não foi possível excluir a tarefa.');
                }
            }
        }
    });
}

function filterTasks() {
    const filterDescElem = document.getElementById('filterDesc');
    const filterGrupoElem = document.getElementById('filterGrupo');
    const filterStatusElem = document.getElementById('filterStatus');

    if (!filterDescElem || !filterGrupoElem || !filterStatusElem) return;

    const descFilter = filterDescElem.value.toLowerCase();
    const grupoFilter = filterGrupoElem.value;
    const statusFilter = filterStatusElem.value;
    const groups = document.querySelectorAll('.task-group');

    groups.forEach(group => {
        let hasVisibleTasks = false;
        const gName = group.getAttribute('data-grupo');
        const rows = group.querySelectorAll('.task-row');

        rows.forEach(row => {
            const rDesc = row.getAttribute('data-desc');
            const rStatus = row.getAttribute('data-status');
            const matchDesc = rDesc.includes(descFilter);
            const matchGrupo = (grupoFilter === "" || gName === grupoFilter);
            const matchStatus = (statusFilter === "" || rStatus === statusFilter);

            if (matchDesc && matchGrupo && matchStatus) {
                row.classList.remove('hidden');
                row.classList.add('flex');
                hasVisibleTasks = true;
            } else {
                row.classList.remove('flex');
                row.classList.add('hidden');
            }
        });
        group.style.display = hasVisibleTasks ? 'block' : 'none';
    });
}

function clearFilters() {
    const filterDescElem = document.getElementById('filterDesc');
    const filterGrupoElem = document.getElementById('filterGrupo');
    const filterStatusElem = document.getElementById('filterStatus');

    if (filterDescElem) filterDescElem.value = '';
    if (filterGrupoElem) filterGrupoElem.selectedIndex = 0;
    if (filterStatusElem) filterStatusElem.selectedIndex = 0;
    filterTasks();
}

// AJAX Interceptors for Task Actions
async function submitAjaxForm(url, formData) {
    const response = await fetch(url, {
        method: 'POST',
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: formData
    });
    if (!response.ok) {
        throw new Error('Erro na requisição');
    }
    return await response.json();
}

function updateTaskRowStatus(row, status) {
    row.setAttribute('data-status', status);
    
    // Update badge status
    const badge = row.querySelector('.min-w-0 span[class*="badge-"]');
    if (badge) {
        badge.className = ''; // Reset classes
        if (status === 'PENDENTE') {
            badge.className = 'badge-warning';
        } else if (status === 'INICIADO') {
            badge.className = 'badge-success';
        } else {
            badge.className = 'badge-neutral opacity-60';
        }
        badge.textContent = status;
    }

    // Update text formatting
    const descSpan = row.querySelector('.min-w-0 span.block');
    if (descSpan) {
        if (status === 'FINALIZADO') {
            descSpan.classList.add('text-text-muted', 'line-through');
            descSpan.classList.remove('text-text-heading');
        } else {
            descSpan.classList.remove('text-text-muted', 'line-through');
            descSpan.classList.add('text-text-heading');
        }
    }

    // Update main status button
    const checkForm = row.querySelector('form[action*="/concluir"], form[action*="/iniciar"]');
    const checkBtn = checkForm ? checkForm.querySelector('button') : null;
    if (checkForm && checkBtn) {
        const taskId = checkForm.action.split('/').pop();
        if (status === 'FINALIZADO') {
            checkForm.action = "/tasks/iniciar/" + taskId;
            checkBtn.className = "relative flex-shrink-0 w-6 h-6 rounded border flex items-center justify-center transition-all duration-200 after:absolute after:-inset-2.5 after:content-[''] bg-success border-success text-white";
            checkBtn.innerHTML = '<i class="ph-bold ph-check"></i>';
        } else if (status === 'INICIADO') {
            checkForm.action = "/tasks/concluir/" + taskId;
            checkBtn.className = "relative flex-shrink-0 w-6 h-6 rounded border flex items-center justify-center transition-all duration-200 after:absolute after:-inset-2.5 after:content-[''] bg-success border-success text-white animate-pulse";
            checkBtn.innerHTML = '<i class="ph-bold ph-play"></i>';
        } else {
            checkForm.action = "/tasks/concluir/" + taskId;
            checkBtn.className = "relative flex-shrink-0 w-6 h-6 rounded border flex items-center justify-center transition-all duration-200 after:absolute after:-inset-2.5 after:content-[''] border-text-muted hover:border-text-normal text-transparent hover:text-text-normal";
            checkBtn.innerHTML = '<i class="ph-bold ph-check"></i>';
        }
    }

    // Update separate play button form visibility
    const playForm = row.querySelector('.play-btn-form');
    if (playForm) {
        if (status === 'PENDENTE') {
            playForm.classList.remove('hidden');
        } else {
            playForm.classList.add('hidden');
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {

    document.addEventListener('submit', async (e) => {
        const form = e.target;
        const isStatusToggle = form.closest('.task-row') && (form.action.includes('/concluir/') || form.action.includes('/iniciar/'));
        const isEditForm = form.id === 'formEditTarefa';

        if (isStatusToggle) {
            e.preventDefault();
            const row = form.closest('.task-row');
            try {
                const data = await submitAjaxForm(form.action, new FormData(form));
                if (data.success) {
                    updateTaskRowStatus(row, data.status);
                    if (window.AppUI && window.AppUI.toast) {
                        window.AppUI.toast('success', 'Status da tarefa atualizado.');
                    }
                }
            } catch (err) {
                console.error(err);
                if (window.AppUI && window.AppUI.toast) {
                    window.AppUI.toast('error', 'Não foi possível atualizar o status.');
                }
            }
        } else if (isEditForm) {
            e.preventDefault();
            try {
                const taskId = form.action.split('/').pop();
                const editBtn = document.querySelector(`.task-row button[data-id="${taskId}"]`);
                const oldGroupId = editBtn ? editBtn.getAttribute('data-grupo') : null;

                const data = await submitAjaxForm(form.action, new FormData(form));
                if (data.success) {
                    const newGroupId = String(data.task.grupo_id);
                    if (oldGroupId !== newGroupId) {
                        // Reload if group changed to re-render groupings
                        window.location.reload();
                        return;
                    }

                    const btn = document.querySelector(`.task-row button[data-id="${taskId}"]`);
                    if (btn) {
                        const row = btn.closest('.task-row');
                        const descSpan = row.querySelector('span.block');
                        if (descSpan) {
                            descSpan.textContent = data.task.descricao;
                        }

                        const editBtns = row.querySelectorAll('button[data-id]');
                        editBtns.forEach(b => {
                            b.setAttribute('data-desc', data.task.descricao);
                            b.setAttribute('data-grupo', data.task.grupo_id);
                            b.setAttribute('data-status', data.task.status);
                        });

                        updateTaskRowStatus(row, data.task.status);
                    }

                    AppUI.toggleModal('modalEditTarefa', false);
                    if (window.AppUI && window.AppUI.toast) {
                        window.AppUI.toast('success', 'Tarefa atualizada com sucesso.');
                    }
                }
            } catch (err) {
                console.error(err);
                if (window.AppUI && window.AppUI.toast) {
                    window.AppUI.toast('error', 'Não foi possível salvar as alterações.');
                }
            }
        }
    });
});
