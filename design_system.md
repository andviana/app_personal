# DayLog - Design System (Minimal Light Theme)

Este documento estabelece o Design System e o padrão visual da aplicação **DayLog**: uma interface clara, minimalista e coesa, com uma única cor de destaque. Ele serve como referência técnica para garantir consistência visual em todos os templates HTML/Jinja2 e arquivos JavaScript da aplicação.

> Histórico: a aplicação usava um tema escuro "estilo Discord" com uma cor de destaque diferente por módulo. Esse tema foi substituído por este sistema claro e unificado — ver o Relatório de Auditoria UI/UX para o racional da mudança.

---

## 🎨 Paleta de Cores

Tokens definidos em `tailwind.config.js` (`theme.extend.colors`):

| Token | Valor | Função |
| :--- | :--- | :--- |
| `bg-primary` / `text-primary` | `#4f46e5` (indigo-600) | **Única** cor de destaque: CTAs, links de ação, estado ativo da navegação, foco de formulário |
| `bg-primary-hover` | `#4338ca` | Hover de elementos primários |
| `bg-primary-active` | `#3730a3` | Active/pressed de elementos primários |
| `bg-primary-light` | `#eef2ff` | Fundos suaves com tom de destaque (ex: item de navegação ativo) |
| `bg-surface` | `#ffffff` | Cards, modais, cabeçalhos — a "superfície" que se destaca do fundo |
| `bg-surface-hover` | `#f8fafc` (slate-50) | Hover sutil sobre superfícies brancas |
| `bg-surface-sunken` | `#f1f5f9` (slate-100) | Áreas rebaixadas: inputs, wells, badges neutros |
| `bg-background` | `#f8fafc` (slate-50) | Fundo geral da página (atrás dos cards) |
| `text-text-heading` | `#0f172a` (slate-900) | Títulos e texto de alta ênfase |
| `text-text-normal` | `#334155` (slate-700) | Texto corrido |
| `text-text-muted` | `#64748b` (slate-500) | Texto secundário, legendas |
| `bg-success` / `text-success` | `#16a34a` | Estado positivo/concluído |
| `bg-danger` / `text-danger` | `#dc2626` | Estado de erro/exclusão |
| `bg-warning` / `text-warning` | `#d97706` | Estado de atenção/pendente |

Bordas usam a escala neutra padrão do Tailwind (`border-slate-200`) — não há token de borda dedicado; a separação entre elementos prioriza contraste de fundo (`bg-surface` sobre `bg-background`) e sombras leves (`shadow-sm`) em vez de bordas pesadas.

**Regra de ouro:** nenhuma cor arbitrária (`bg-[#hex]`) deve ser usada para elementos de UI/ação. Cores de tag/etiqueta definidas pelo usuário (ex: cores de tags de snippets) são a única exceção — são dados do usuário, não decisão de marca.

---

## 1. Tipografia e Espaçamento

*   **H1 (Título de Página)**: `text-2xl md:text-3xl font-bold text-text-heading tracking-tight` — gerado automaticamente pelo macro `page_header`.
*   **H2 (Título de Seção/Card)**: `text-base md:text-lg font-semibold text-text-heading`
*   **H3 (Metadados/Labels técnicas)**: `text-xs font-semibold text-text-muted`
*   **Texto Corrido**: `text-sm text-text-normal leading-relaxed`
*   **Texto Auxiliar**: `text-xs text-text-muted`

Maiúsculas (`uppercase`) e `tracking-widest` são usadas com moderação — apenas em rótulos muito curtos (badges, eyebrows), nunca em títulos, botões ou parágrafos.

---

## 2. Superfícies e Cards

*   `bg-surface border border-slate-200/70 rounded-xl p-5 hover:border-slate-300 shadow-sm` → classe utilitária `.card-container`
*   Listas de itens dentro de um card usam `divide-y divide-slate-100` em vez de bordas individuais por linha.

---

## 3. Formulários

Classes utilitárias (`app/static/css/input.css`, `@layer components`):

*   `.form-label` — rótulo discreto, `text-xs font-medium text-text-muted`
*   `.form-input` — fundo `surface-sunken`, sem borda visível em repouso, foco com anel `primary/20`
*   `.form-textarea` — mesma linguagem do input, `min-h-[100px]`
*   `.form-select` — `.form-input` + seta customizada (usar macro `form_select`)
*   `.form-checkbox` — checkbox compacto com acento `primary`
*   `.form-input-error` / `.form-error-msg` — estado de erro em `danger`

---

## 4. Botões — 3 Níveis

Todos compartilham base (`.btn-base`): mesma transição, mesmo `focus:ring`, mesmo `active:scale`.

| Nível | Classe | Uso |
| :--- | :--- | :--- |
| **Primário** | `.btn-primary` | Fundo `primary` preenchido, texto branco. **Uma ação principal por tela.** |
| **Secundário** | `.btn-secondary` | Fundo `surface`, borda `slate-200`, texto escuro. Ações de apoio (Cancelar, Filtrar). |
| **Terciário/Ghost** | `.btn-ghost` | Sem fundo/borda; ganha `bg-surface-sunken` no hover. Ações discretas em listas/toolbars. |

Tamanhos: `.btn-sm` (h-8), `.btn-md` (h-11, padrão), `.btn-lg` (h-12). Todos usam `rounded-lg`.

Botões de ícone: `.btn-icon-sm` / `.btn-icon-md` (com borda) e `.btn-icon` / `.btn-icon-danger` (para toolbars de card).

---

## 5. Badges

`.badge-primary`, `.badge-success`, `.badge-warning`, `.badge-danger`, `.badge-neutral` — todas em formato `rounded-full`, fundo tonalizado a 10% de opacidade, texto na cor sólida correspondente.

---

## 6. Navegação

*   **Sidebar (desktop) / Drawer (mobile) / Bottom nav (mobile)**: compartilham a mesma lista de itens (`nav_items` em `base.html`). O item ativo usa **sempre** `bg-primary-light text-primary` (ou `text-primary` puro na bottom nav) — nunca uma cor por módulo.
*   **Botão Voltar**: `.btn-back` — link discreto com ícone que desliza no hover, sempre acima do título da página.
*   **Cabeçalho de página**: use o macro `page_header(title, icon=..., subtitle=..., badge=...)` de `macros/components.html`. Título e ícone à esquerda; ações (via `{% call %}`) à direita, com o botão primário sempre por último (mais à direita).
*   **Rodapé de formulário**: botão secundário/ghost ("Cancelar"/"Voltar") sempre à esquerda do botão primário ("Salvar"), usando `order-2 md:order-1` / `order-1 md:order-2` para manter o CTA primário como o elemento mais natural de alcançar em mobile (topo) e desktop (direita).

---

## 7. Macros disponíveis (`app/templates/macros/components.html`)

`btn_primary`, `btn_secondary`, `btn_ghost`, `form_input`, `form_textarea`, `form_select`, `form_checkbox`, `alert`, `card`, `page_header`, `empty_state`.

Sempre prefira os macros a classes Tailwind soltas — eles são a fonte única de verdade do sistema.

---

## 8. Exceções documentadas

*   **Editor de Markdown (EasyMDE)** em `snippets/new.html` e `snippets/edit.html` mantém tema escuro próprio (convenção comum de editores de código, independente do tema da aplicação).
*   **Cores de tags de Snippets** (`premium_colors` em `snippets/index.html`) são uma paleta de 12 cores para o usuário rotular conteúdo — não fazem parte da paleta de marca.
*   **Blocos de código (Pygments/`codehilite`)** e o parser de Markdown mantêm sua própria paleta de sintaxe, sempre sobre fundo claro.
