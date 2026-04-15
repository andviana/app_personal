/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/templates/**/*.html",
    "./app/static/js/**/*.js"
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#5865F2',
          hover: '#4752C4',
          active: '#3C45A5'
        },
        discord: {
          100: '#1e1f22',
          200: '#2b2d31',
          300: '#313338',
          400: '#383a40',
          modal: '#313338',
        },
        text: {
          normal: '#dbdee1',
          muted: '#949ba4',
          heading: '#f2f3f5',
        },
        success: '#23a559',
        danger: '#da373c',
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
