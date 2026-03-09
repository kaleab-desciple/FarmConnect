import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import en from './locales/en/translation.json';
import am from './locales/am/translation.json';
import om from './locales/om/translation.json';

const resources = {
  en: { translation: en },
  am: { translation: am },
  om: { translation: om },
};

// Get saved language or default to browser language
const getSavedLanguage = (): string => {
  const saved = localStorage.getItem('language');
  if (saved && ['en', 'am', 'om'].includes(saved)) {
    return saved;
  }
  
  // Check browser language
  const browserLang = navigator.language.split('-')[0];
  if (['en', 'am', 'om'].includes(browserLang)) {
    return browserLang;
  }
  
  return 'en';
};

i18n
  .use(initReactI18next)
  .init({
    resources,
    lng: getSavedLanguage(),
    fallbackLng: 'en',
    interpolation: {
      escapeValue: false, // React already handles XSS
    },
    react: {
      useSuspense: false,
    },
  });

// Save language preference when changed
i18n.on('languageChanged', (lng) => {
  localStorage.setItem('language', lng);
  document.documentElement.lang = lng;
});

export default i18n;
