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
        toggleBtn.innerHTML = '<i class="ph-bold ph-plus text-lg text-primary-DEFAULT"></i>';
        toggleBtn.classList.replace('bg-discord-100', 'bg-discord-200');
        toggleBtn.classList.add('border-discord-400');
    } else {
        filterBar.classList.add('hidden');
        taskForm.classList.remove('hidden');
        toggleBtn.innerHTML = '<i class="ph-bold ph-magnifying-glass text-lg"></i> <span class="hidden md:inline">Pesquisar</span>';
        toggleBtn.classList.replace('bg-discord-200', 'bg-discord-100');
        toggleBtn.classList.remove('border-discord-400');
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

    const modal = document.getElementById('modalEditTarefa');
    if (modal) modal.classList.remove('hidden');
}

function confirmDeleteTask(id, descricao) {
    if (typeof Swal === 'undefined') {
        if (confirm(`Deseja realmente remover a tarefa "${descricao}"?`)) {
            const form = document.getElementById('delete-task-form');
            form.action = "/tasks/delete/" + id;
            form.submit();
        }
        return;
    }

    Swal.fire({
        title: 'Excluir Tarefa?',
        text: `Deseja realmente remover a tarefa "${descricao}"?`,
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#da373c',
        cancelButtonColor: '#4e5058',
        confirmButtonText: 'Sim, excluir!',
        cancelButtonText: 'Cancelar',
        reverseButtons: true,
        customClass: {
            popup: 'discord-theme',
            confirmButton: 'rounded-xl px-6 py-3 font-bold',
            cancelButton: 'rounded-xl px-6 py-3 font-bold'
        }
    }).then((result) => {
        if (result.isConfirmed) {
            const form = document.getElementById('delete-task-form');
            form.action = "/tasks/delete/" + id;
            form.submit();
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
