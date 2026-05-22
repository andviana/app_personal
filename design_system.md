# DayLog - Design System (Discord Dark Theme)

Este documento estabelece o Design System e o padrão visual para a aplicação **DayLog**, estritamente baseado no tema escuro do Discord. Ele serve como referência técnica para garantir consistência visual e integridade estrutural em todos os templates HTML/Jinja2 e arquivos Javascript da aplicação.

---

## 🎨 Paleta de Cores e Temas

Os seguintes tokens de cores estão definidos na configuração do Tailwind (`tailwind.config.js`):

| Token | Hex | Função / Aplicação |
| :--- | :--- | :--- |
| `bg-discord-100` | `#1e1f22` | Superfície mais escura (Sidebar de servidores, inputs sem foco/com foco) |
| `bg-discord-200` | `#2b2d31` | Superfície média (Sidebar de canais, cabeçalhos de tabelas, cards) |
| `bg-discord-300` | `#313338` | Fundo principal da aplicação (Área de chat principal) |
| `bg-discord-400` | `#383a40` | Superfícies com hover, destaques secundários |
| `bg-discord-modal`| `#313338` | Fundo de modais |
| `text-text-heading` | `#f2f3f5` | Títulos, cabeçalhos e textos de alta legibilidade (branco/cinza muito claro) |
| `text-text-normal`  | `#dbdee1` | Texto principal corrido, parágrafos |
| `text-text-muted`   | `#949ba4` | Textos secundários, legendas, descrições secundárias |
| `bg-primary-DEFAULT`| `#5865F2` | Cor principal (Blurple do Discord), botões primários |
| `bg-success`        | `#23a559` | Status positivo, concluído, botões de sucesso |
| `bg-danger`         | `#da373c` | Status de erro, cancelamento, botões de perigo |

---

## 1. Tipografia e Espaçamento (Layout Base)

### Padrões Adotados
*   **H1 (Título Principal)**: Utilizado em cabeçalhos de páginas principais e dashboards.
*   **H2 (Subtítulo de Páginas / Título de Seções)**: Utilizado para subdividir seções ou títulos em cards.
*   **H3 (Títulos de Metadados / Labels Técnicas)**: Utilizado em seções auxiliares e pequenos metadados.
*   **Texto Corrido (Padrão)**: Estilo para leituras de parágrafo gerais.
*   **Texto Auxiliar (Muted)**: Estilo para datas, notas de rodapé e informações adicionais de baixa prioridade.
*   **Espaçamento Base de Layout**: Espaçamentos estruturais padronizados em layouts de seções ou de páginas inteiras.

### Classes Tailwind
*   **H1**: `text-2xl md:text-3xl font-black text-text-heading tracking-tight`
*   **H2**: `text-lg md:text-xl font-extrabold text-text-heading tracking-wide`
*   **H3**: `text-[10px] md:text-xs font-black uppercase tracking-widest text-text-muted`
*   **Texto Corrido**: `text-sm font-medium text-text-normal leading-relaxed`
*   **Texto Auxiliar**: `text-xs font-semibold text-text-muted`
*   **Section Container**: `py-6 px-4 md:px-8 space-y-6`

### Exemplo Estrutural (HTML)
```html
<section class="py-6 px-4 md:px-8 space-y-6">
    <div class="flex flex-col gap-1">
        <h1 class="text-2xl md:text-3xl font-black text-text-heading tracking-tight">Painel Principal</h1>
        <p class="text-xs font-semibold text-text-muted">Última atualização: hoje às 10:30</p>
    </div>
    
    <div class="space-y-4">
        <h2 class="text-lg md:text-xl font-extrabold text-text-heading tracking-wide">Minhas Tarefas</h2>
        <p class="text-sm font-medium text-text-normal leading-relaxed">
            Aqui você gerencia suas atividades diárias no estilo Discord.
        </p>
    </div>
</section>
```

---

## 2. Superfícies e Cards

### Padrões Adotados
*   **Fundo**: `discord-200` para destaque contra o fundo principal `discord-300`.
*   **Borda**: Borda ultrafina semitransparente para separação sem peso visual.
*   **Hover**: Transição suave para `discord-400` com transparência aplicada.

### Classes Tailwind
*   `bg-discord-200 border border-discord-100/10 rounded-xl p-5 hover:bg-discord-400/30 transition-all duration-200 shadow-md`

### Exemplo Estrutural (HTML)
```html
<div class="bg-discord-200 border border-discord-100/10 rounded-xl p-5 hover:bg-discord-400/30 transition-all duration-200 shadow-md">
    <div class="flex justify-between items-start gap-4">
        <div class="space-y-1">
            <h3 class="text-[10px] md:text-xs font-black uppercase tracking-widest text-text-muted">Lista de Compras</h3>
            <h2 class="text-lg md:text-xl font-extrabold text-text-heading tracking-wide">Mercado Mensal</h2>
        </div>
        <!-- Elemento de status ou ícone -->
    </div>
</div>
```

---

## 3. Formulários e Inputs

### Padrões Adotados
*   **Labels**: Sempre em caixa alta, espaçadas e em tons acinzentados (`text-text-muted`).
*   **Inputs / Textareas / Selects**: Fundo escuro (`discord-100`), sem bordas pesadas, com foco em anel azul do Discord (`ring-primary-DEFAULT`).
*   **Checkboxes**: Foco e visual minimalista.

### Classes Tailwind
*   **Label**: `text-[10px] md:text-xs font-black uppercase tracking-widest text-text-muted mb-2 block`
*   **Input / Select**: `w-full h-11 px-4 bg-discord-100 border border-discord-100 hover:bg-discord-100/80 text-text-normal placeholder:text-text-muted/40 font-semibold text-sm rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-DEFAULT transition-all duration-200`
*   **Textarea**: `w-full p-4 bg-discord-100 border border-discord-100 hover:bg-discord-100/80 text-text-normal placeholder:text-text-muted/40 font-semibold text-sm rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-DEFAULT transition-all duration-200 min-h-[100px]`
*   **Checkbox**: `w-5 h-5 bg-discord-100 border border-discord-400 text-primary-DEFAULT rounded focus:ring-primary-DEFAULT focus:ring-2 focus:ring-offset-0 transition-all duration-200 cursor-pointer`
*   **Input com Erro**: `border-danger focus:ring-danger text-text-heading`
*   **Mensagem de Erro**: `text-xs font-semibold text-danger mt-1.5 block`

### Exemplo Estrutural (HTML)
```html
<form class="space-y-4">
    <!-- Input Padrão -->
    <div class="flex flex-col">
        <label for="titulo" class="text-[10px] md:text-xs font-black uppercase tracking-widest text-text-muted mb-2 block">Título da Tarefa</label>
        <input type="text" id="titulo" name="titulo" placeholder="Ex: Resolver pendências do deploy" 
            class="w-full h-11 px-4 bg-discord-100 border border-discord-100 hover:bg-discord-100/80 text-text-normal placeholder:text-text-muted/40 font-semibold text-sm rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-DEFAULT transition-all duration-200">
    </div>

    <!-- Input com Erro -->
    <div class="flex flex-col">
        <label for="email" class="text-[10px] md:text-xs font-black uppercase tracking-widest text-text-muted mb-2 block">E-mail</label>
        <input type="email" id="email" name="email" value="email-invalido@" 
            class="w-full h-11 px-4 bg-discord-100 border border-danger hover:bg-discord-100/80 text-text-heading font-semibold text-sm rounded-lg focus:outline-none focus:ring-2 focus:ring-danger transition-all duration-200">
        <span class="text-xs font-semibold text-danger mt-1.5 block">Por favor, insira um e-mail válido.</span>
    </div>

    <!-- Checkbox Personalizado -->
    <div class="flex items-center gap-3">
        <input type="checkbox" id="lembrar" name="lembrar" 
            class="w-5 h-5 bg-discord-100 border border-discord-400 text-primary-DEFAULT rounded focus:ring-primary-DEFAULT focus:ring-2 focus:ring-offset-0 transition-all duration-200 cursor-pointer">
        <label for="lembrar" class="text-sm font-semibold text-text-normal cursor-pointer select-none">Manter conectado</label>
    </div>
</form>
```

---

## 4. Botões e Ações

### Classes Adotadas (Tipos e Estados)
*   **Primary (Blurple)**: `px-4 h-10 md:h-11 bg-primary-DEFAULT hover:bg-primary-hover active:bg-primary-active text-white font-bold text-sm rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 flex items-center justify-center gap-2 shadow-sm`
*   **Secondary (Dark Gray)**: `px-4 h-10 md:h-11 bg-discord-400 hover:bg-[#4e5058] active:bg-[#6d6f78] text-text-heading font-bold text-sm rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 flex items-center justify-center gap-2 shadow-sm`
*   **Danger (Red)**: `px-4 h-10 md:h-11 bg-danger hover:bg-[#a92b2f] active:bg-[#822023] text-white font-bold text-sm rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 flex items-center justify-center gap-2 shadow-sm`
*   **Success (Green)**: `px-4 h-10 md:h-11 bg-success hover:bg-[#1a7f43] active:bg-[#156334] text-white font-bold text-sm rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 flex items-center justify-center gap-2 shadow-sm`
*   **Ghost (Transparent)**: `px-4 h-10 md:h-11 bg-transparent hover:bg-discord-400/40 text-text-muted hover:text-text-heading font-bold text-sm rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 flex items-center justify-center gap-2`
*   **Icon Button (Edição/Padrão)**: `w-9 h-9 flex items-center justify-center bg-discord-300 hover:bg-discord-400 text-text-muted hover:text-text-heading rounded-lg transition-all duration-200 shadow-sm`
*   **Icon Button (Exclusão/Perigo)**: `w-9 h-9 flex items-center justify-center bg-discord-300 hover:bg-danger text-text-muted hover:text-white rounded-lg transition-all duration-200 shadow-sm`

### Exemplo Estrutural (HTML)
```html
<div class="flex flex-wrap gap-3">
    <!-- Primário com ícone -->
    <button class="px-4 h-11 bg-primary-DEFAULT hover:bg-primary-hover active:bg-primary-active text-white font-bold text-sm rounded-lg transition-all duration-200 flex items-center justify-center gap-2 shadow-sm">
        <i class="ph-bold ph-plus"></i>
        <span>Adicionar Item</span>
    </button>

    <!-- Secundário -->
    <button class="px-4 h-11 bg-discord-400 hover:bg-[#4e5058] active:bg-[#6d6f78] text-text-heading font-bold text-sm rounded-lg transition-all duration-200 shadow-sm">
        Cancelar
    </button>

    <!-- Icon Buttons (Ações de linha) -->
    <div class="flex items-center gap-1.5">
        <button class="w-9 h-9 flex items-center justify-center bg-discord-300 hover:bg-discord-400 text-text-muted hover:text-text-heading rounded-lg transition-all duration-200 shadow-sm" title="Editar">
            <i class="ph-bold ph-pencil-simple text-base"></i>
        </button>
        <button class="w-9 h-9 flex items-center justify-center bg-discord-300 hover:bg-danger text-text-muted hover:text-white rounded-lg transition-all duration-200 shadow-sm" title="Excluir">
            <i class="ph-bold ph-trash text-base"></i>
        </button>
    </div>
</div>
```

---

## 5. Navegação Interna (Tabs / Filtros)

### Padrões Adotados
*   **Container**: Fundo escuro completo (`discord-100`) para simular uma barra estruturada de filtros.
*   **Items**: Destaque sutil com sombra apenas no item ativo.

### Classes Tailwind
*   **Container**: `flex items-center gap-1.5 bg-discord-100 p-1.5 rounded-lg w-max max-w-full overflow-x-auto`
*   **Active Tab**: `px-4 py-2 bg-discord-400 text-text-heading font-bold text-xs md:text-sm rounded-md transition-all duration-200 shadow-sm`
*   **Inactive Tab**: `px-4 py-2 text-text-muted hover:bg-discord-200/50 hover:text-text-normal font-bold text-xs md:text-sm rounded-md transition-all duration-200`

### Exemplo Estrutural (HTML)
```html
<nav class="flex items-center gap-1.5 bg-discord-100 p-1.5 rounded-lg w-max max-w-full overflow-x-auto">
    <button class="px-4 py-2 bg-discord-400 text-text-heading font-bold text-xs md:text-sm rounded-md transition-all duration-200 shadow-sm">
        Todos
    </button>
    <button class="px-4 py-2 text-text-muted hover:bg-discord-200/50 hover:text-text-normal font-bold text-xs md:text-sm rounded-md transition-all duration-200">
        Pendentes
    </button>
    <button class="px-4 py-2 text-text-muted hover:bg-discord-200/50 hover:text-text-normal font-bold text-xs md:text-sm rounded-md transition-all duration-200">
        Concluídos
    </button>
</nav>
```

---

## 6. Feedback Visual

### Badges / Tags

#### Classes Adotadas (Variantes)
*   **Success (Verde)**: `px-2 py-0.5 bg-success/15 text-success border border-success/25 rounded text-[10px] md:text-[11px] font-extrabold uppercase tracking-wider`
*   **Warning (Amarelo)**: `px-2 py-0.5 bg-[#f0b232]/15 text-[#f0b232] border border-[#f0b232]/25 rounded text-[10px] md:text-[11px] font-extrabold uppercase tracking-wider`
*   **Danger (Vermelho)**: `px-2 py-0.5 bg-danger/15 text-danger border border-danger/25 rounded text-[10px] md:text-[11px] font-extrabold uppercase tracking-wider`
*   **Neutral (Cinza)**: `px-2 py-0.5 bg-discord-400 text-text-normal border border-discord-400/50 rounded text-[10px] md:text-[11px] font-extrabold uppercase tracking-wider`

#### Exemplo Estrutural (HTML)
```html
<div class="flex items-center gap-2">
    <span class="px-2 py-0.5 bg-success/15 text-success border border-success/25 rounded text-[11px] font-extrabold uppercase tracking-wider">Concluído</span>
    <span class="px-2 py-0.5 bg-[#f0b232]/15 text-[#f0b232] border border-[#f0b232]/25 rounded text-[11px] font-extrabold uppercase tracking-wider">Pendente</span>
    <span class="px-2 py-0.5 bg-discord-400 text-text-normal border border-discord-400/50 rounded text-[11px] font-extrabold uppercase tracking-wider">Neutro</span>
</div>
```

---

### Modais (Estrutura do Discord)

#### Classes Adotadas (Estrutura)
*   **Backdrop**: `fixed inset-0 bg-black/70 backdrop-blur-sm z-[999] flex items-center justify-center p-4`
*   **Container**: `bg-discord-modal w-full max-w-lg rounded-xl shadow-2xl border border-discord-100/30 flex flex-col overflow-hidden`
*   **Header**: `px-6 py-4 bg-discord-200 flex items-center justify-between border-b border-discord-100/10`
*   **Body**: `p-6 space-y-4 text-text-normal text-sm font-medium`
*   **Footer**: `px-6 py-4 bg-discord-200 flex items-center justify-end gap-3 border-t border-discord-100/10`

#### Exemplo Estrutural (HTML)
```html
<!-- Modal Backdrop -->
<div class="fixed inset-0 bg-black/70 backdrop-blur-sm z-[999] flex items-center justify-center p-4">
    <!-- Modal Container -->
    <div class="bg-discord-modal w-full max-w-lg rounded-xl shadow-2xl border border-discord-100/30 flex flex-col overflow-hidden animate-fade-in">
        
        <!-- Header -->
        <div class="px-6 py-4 bg-discord-200 flex items-center justify-between border-b border-discord-100/10">
            <h3 class="text-lg font-bold text-text-heading">Excluir Snippet</h3>
            <button class="text-text-muted hover:text-text-heading transition-colors" title="Fechar">
                <i class="ph-bold ph-x text-lg"></i>
            </button>
        </div>
        
        <!-- Body -->
        <div class="p-6 text-text-normal text-sm font-medium">
            Tem certeza de que deseja excluir permanentemente o snippet <strong class="text-text-heading">"Helper DB Connect"</strong>? Esta ação não poderá ser revertida.
        </div>
        
        <!-- Footer -->
        <div class="px-6 py-4 bg-discord-200 flex items-center justify-end gap-3 border-t border-discord-100/10">
            <button class="px-4 h-10 bg-transparent hover:bg-discord-400/40 text-text-muted hover:text-text-heading font-bold text-sm rounded-lg transition-all duration-200">
                Cancelar
            </button>
            <button class="px-4 h-10 bg-danger hover:bg-[#a92b2f] active:bg-[#822023] text-white font-bold text-sm rounded-lg transition-all duration-200">
                Excluir
            </button>
        </div>
        
    </div>
</div>
```
