/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/templates/**/*.html",
    "./app/static/js/**/*.js"
  ],
  theme: {
    extend: {
      colors: {
        // Única cor de destaque da aplicação. Usada em botões primários,
        // links de ação, estado ativo da navegação e focos de formulário.
        primary: {
          DEFAULT: '#4f46e5', // indigo-600
          hover: '#4338ca',   // indigo-700
          active: '#3730a3',  // indigo-800
          light: '#eef2ff',   // indigo-50 (fundos suaves, badges, tints)
        },

        // Superfícies: cards, modais, cabeçalhos de tabela, inputs.
        surface: {
          DEFAULT: '#ffffff', // cards e modais
          hover: '#f8fafc',   // slate-50 — hover sutil sobre superfícies brancas
          sunken: '#f1f5f9',  // slate-100 — áreas "rebaixadas": inputs, wells, sidebar
        },

        // Fundo geral da página (por trás dos cards).
        background: '#f8fafc', // slate-50

        // Textos — única escala de cinza para toda a aplicação (slate).
        text: {
          heading: '#0f172a', // slate-900
          normal: '#334155',  // slate-700
          muted: '#64748b',   // slate-500
        },

        // Cores de estado (semânticas, não decorativas).
        success: {
          DEFAULT: '#16a34a', // green-600
          hover: '#15803d',   // green-700
        },
        danger: {
          DEFAULT: '#dc2626', // red-600
          hover: '#b91c1c',   // red-700
        },
        warning: {
          DEFAULT: '#d97706', // amber-600
          hover: '#b45309',   // amber-700
        },
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
