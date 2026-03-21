/**
 * WWC i18n — Language switcher utility
 * Supported languages: fr (default), en, ar
 * Usage:
 *   import { getLang, setLang, t, tObj } from '/static/js/i18n.js';
 *   tObj(product, 'name')  → product.name_en or product.name_ar or product.name
 */

const SUPPORTED = ['fr', 'en', 'ar'];
const STORAGE_KEY = 'wwc_lang';

export function getLang() {
    const stored = localStorage.getItem(STORAGE_KEY);
    return SUPPORTED.includes(stored) ? stored : 'fr';
}

export function setLang(lang) {
    if (!SUPPORTED.includes(lang)) return;
    localStorage.setItem(STORAGE_KEY, lang);
    document.documentElement.lang = lang;
    document.documentElement.dir = lang === 'ar' ? 'rtl' : 'ltr';
}

/**
 * Get the localised value of a field from an API object.
 * e.g. tObj(product, 'name') returns product.name_en when lang=en,
 * falling back to product.name if the translated field is empty.
 */
export function tObj(obj, field) {
    const lang = getLang();
    if (!obj) return '';
    if (lang === 'fr') return obj[field] || '';
    const localised = obj[`${field}_${lang}`];
    return (localised && localised.trim()) ? localised : (obj[field] || '');
}

/** Static UI strings */
const UI = {
    fr: {
        shop: 'Boutique',
        impact: 'Notre Impact',
        donate: 'Faire un don',
        box: 'Composer ma box',
        search: '🔍 Rechercher un produit…',
        cart: 'Mon panier',
        login: 'Connexion',
        logout: 'Déconnexion',
        account: 'Mon compte',
        addToCart: 'Ajouter au panier',
        noProducts: 'Aucun produit trouvé.',
        loading: 'Chargement…',
    },
    en: {
        shop: 'Shop',
        impact: 'Our Impact',
        donate: 'Donate',
        box: 'Build my box',
        search: '🔍 Search a product…',
        cart: 'My cart',
        login: 'Login',
        logout: 'Logout',
        account: 'My account',
        addToCart: 'Add to cart',
        noProducts: 'No products found.',
        loading: 'Loading…',
    },
    ar: {
        shop: 'المتجر',
        impact: 'تأثيرنا',
        donate: 'تبرع',
        box: 'اصنع صندوقي',
        search: '🔍 ابحث عن منتج…',
        cart: 'سلة التسوق',
        login: 'تسجيل الدخول',
        logout: 'تسجيل الخروج',
        account: 'حسابي',
        addToCart: 'أضف إلى السلة',
        noProducts: 'لا توجد منتجات.',
        loading: 'جارٍ التحميل…',
    },
};

export function t(key) {
    const lang = getLang();
    return (UI[lang] && UI[lang][key]) || UI['fr'][key] || key;
}

/**
 * Render the language switcher widget HTML.
 * The caller should inject it into the DOM and call initLangSwitcher() after.
 */
export function langSwitcherHTML() {
    const lang = getLang();
    const btns = SUPPORTED.map(l => {
        const label = { fr: 'FR', en: 'EN', ar: 'ع' }[l];
        const active = l === lang;
        return `<button onclick="window.__wwcSetLang('${l}')"
            style="padding:5px 10px;border:none;cursor:pointer;font-size:13px;font-weight:700;
            background:${active ? '#1c345e' : 'transparent'};
            color:${active ? 'white' : '#191919'};
            border-radius:6px;transition:all 0.15s;"
            data-lang="${l}">${label}</button>`;
    }).join('');
    return `<div id="lang-switcher"
        style="display:flex;background:var(--wwc-bg-light,#f5f5f5);border-radius:8px;
        overflow:hidden;border:1px solid var(--wwc-border,#ececec);gap:2px;padding:2px;">
        ${btns}
    </div>`;
}

/** Call once on page load — wires up the global setter used by inline onclick */
export function initLangSwitcher(onChangeCb) {
    // Apply stored lang immediately
    const lang = getLang();
    document.documentElement.lang = lang;
    document.documentElement.dir = lang === 'ar' ? 'rtl' : 'ltr';

    window.__wwcSetLang = (newLang) => {
        setLang(newLang);
        // Update switcher button styles without full page reload
        document.querySelectorAll('#lang-switcher button[data-lang]').forEach(btn => {
            const active = btn.dataset.lang === newLang;
            btn.style.background = active ? '#1c345e' : 'transparent';
            btn.style.color = active ? 'white' : '#191919';
        });
        if (onChangeCb) onChangeCb(newLang);
    };
}
