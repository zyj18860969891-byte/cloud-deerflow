import createMiddleware from 'next-intl/middleware';

const locales = ['en', 'zh'];
const defaultLocale = 'en';

export default createMiddleware({
  locales,
  defaultLocale,
  localePrefix: 'never' // Don't add locale prefix to URLs
});

export const config = {
  matcher: ['/((?!api|_next|_vercel|.*\\..*).*)']
};