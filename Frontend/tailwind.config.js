/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                'palace-night': '#0a0e1a',
                'palace-deep':  '#060a14',
                'indigo-mid':   '#1a1f3a',
                'indigo-soft':  '#2a3060',
                'gold':         '#D4AF37',
                'gold-light':   '#F0D060',
                'gold-dim':     '#8B7320',
                'cream':        '#FFF8DC',
                'amber-warm':   '#C8944A',
                'moonbeam':     '#E0E4F0',
                'lavender':     '#8B82DC',
                'starlight':    '#FFFAE6',
            },
            fontFamily: {
                urdu:  ['"Noto Nastaliq Urdu"', 'serif'],
                latin: ['Inter', '-apple-system', 'sans-serif'],
            },
            animation: {
                'pulse-slow':      'pulse-slow 4s ease-in-out infinite',
                'quill-blink':     'quill-blink 0.8s step-end infinite',
                'fade-in':         'fade-in 0.8s ease-out both',
                'slide-up':        'slide-up 0.7s ease-out both',
                'float':           'float 6s ease-in-out infinite',
                'float-gentle':    'float-gentle 8s ease-in-out infinite',
                'shimmer':         'shimmer 5s ease-in-out infinite',
                'glow-pulse':      'glow-pulse 3s ease-in-out infinite',
                'breathe':         'breathe 4s ease-in-out infinite',
                'border-shimmer':  'border-shimmer 3s ease-in-out infinite',
                'typing-dot':      'typing-dot 1.4s ease-in-out infinite',
                'star-pop':        'star-pop 0.4s cubic-bezier(0.34,1.56,0.64,1) both',
                'slide-in-bot':    'slide-in-bot 0.5s ease-out both',
                'slide-in-user':   'slide-in-user 0.5s ease-out both',
                'completion-glow': 'completion-glow 1.5s ease-out both',
                'entrance-scale':  'entrance-scale 0.6s ease-out both',
            },
            keyframes: {
                'pulse-slow': {
                    '0%, 100%': { opacity: '0.5', transform: 'scale(1)' },
                    '50%':     { opacity: '0.8', transform: 'scale(1.05)' },
                },
                'quill-blink': {
                    '0%, 100%': { opacity: '1' },
                    '50%':     { opacity: '0' },
                },
                'fade-in': {
                    from: { opacity: '0' },
                    to:   { opacity: '1' },
                },
                'slide-up': {
                    from: { opacity: '0', transform: 'translateY(24px)' },
                    to:   { opacity: '1', transform: 'translateY(0)' },
                },
                'float': {
                    '0%, 100%': { transform: 'translateY(0px)' },
                    '50%':     { transform: 'translateY(-10px)' },
                },
                'float-gentle': {
                    '0%, 100%': { transform: 'translateY(0px) rotate(0deg)' },
                    '33%':     { transform: 'translateY(-6px) rotate(0.5deg)' },
                    '66%':     { transform: 'translateY(-3px) rotate(-0.3deg)' },
                },
                'shimmer': {
                    '0%':   { 'background-position': '200% center' },
                    '100%': { 'background-position': '-200% center' },
                },
                'glow-pulse': {
                    '0%, 100%': { 'box-shadow': '0 0 15px rgba(212,175,55,0.08), 0 0 30px rgba(212,175,55,0.03)' },
                    '50%':     { 'box-shadow': '0 0 25px rgba(212,175,55,0.18), 0 0 50px rgba(212,175,55,0.06)' },
                },
                'border-shimmer': {
                    '0%, 100%': { 'border-color': 'rgba(212,175,55,0.12)' },
                    '50%':     { 'border-color': 'rgba(212,175,55,0.35)' },
                },
                'breathe': {
                    '0%, 100%': { opacity: '0.75', filter: 'drop-shadow(0 2px 6px rgba(255,200,80,0.2))' },
                    '50%':     { opacity: '1', filter: 'drop-shadow(0 2px 12px rgba(255,200,80,0.45))' },
                },
                'completion-glow': {
                    '0%':  { 'box-shadow': '0 0 0 rgba(212,175,55,0)' },
                    '30%': { 'box-shadow': '0 0 30px rgba(212,175,55,0.2), 0 0 60px rgba(212,175,55,0.08)' },
                    '100%':{ 'box-shadow': '0 0 0 rgba(212,175,55,0)' },
                },
                'typing-dot': {
                    '0%, 80%, 100%': { opacity: '0.25', transform: 'translateY(0)' },
                    '40%':           { opacity: '1', transform: 'translateY(-6px)' },
                },
                'star-pop': {
                    '0%':   { transform: 'scale(0) rotate(-30deg)', opacity: '0' },
                    '60%':  { transform: 'scale(1.15) rotate(5deg)', opacity: '1' },
                    '100%': { transform: 'scale(1) rotate(0deg)', opacity: '1' },
                },
                'slide-in-bot': {
                    from: { opacity: '0', transform: 'translateX(-16px) scale(0.97)' },
                    to:   { opacity: '1', transform: 'translateX(0) scale(1)' },
                },
                'slide-in-user': {
                    from: { opacity: '0', transform: 'translateX(16px) scale(0.97)' },
                    to:   { opacity: '1', transform: 'translateX(0) scale(1)' },
                },
                'entrance-scale': {
                    from: { opacity: '0', transform: 'scale(0.92)' },
                    to:   { opacity: '1', transform: 'scale(1)' },
                },
            },
        },
    },
    plugins: [],
}
