// Cookie Banner per Casa Obàtálá
// Conforme GDPR - Cookie tecnici + Google Analytics 4 (consenso) + Cloudflare Web Analytics (cookie-free)

// ─── GA4 Consent Mode: default DENIED ───────────────────────────────────────
// Deve girare PRIMA del caricamento del tag gtag.js
window.dataLayer = window.dataLayer || [];
function gtag() { dataLayer.push(arguments); }
gtag('consent', 'default', {
    'analytics_storage': 'denied',
    'ad_storage': 'denied',
    'wait_for_update': 500
});

// Se l'utente aveva già dato consenso in una visita precedente, riattiva subito
if (localStorage.getItem('cookieConsent') === 'accepted') {
    gtag('consent', 'update', { 'analytics_storage': 'granted' });
}
// ─────────────────────────────────────────────────────────────────────────────

(function () {
    // Non mostrare il banner se l'utente ha già scelto
    if (localStorage.getItem('cookieConsent')) {
        return;
    }

    const bannerHTML = `
    <div id="cookie-banner" style="
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background: #fff;
        border-top: 2px solid #8B4513;
        padding: 1rem 1.2rem;
        box-shadow: 0 -4px 20px rgba(0,0,0,0.15);
        z-index: 9999;
        font-family: 'Inter', -apple-system, sans-serif;
    ">
        <div style="max-width: 1200px; margin: 0 auto;">
            <div style="display: flex; flex-wrap: wrap; gap: 1rem; align-items: center; justify-content: space-between;">
                <div style="flex: 1; min-width: 280px;">
                    <p style="font-size: 0.9rem; color: #2a2a2a; margin: 0 0 0.5rem 0; line-height: 1.5;">
                        <strong style="color: #8B4513;">🍪 Questo sito usa cookie tecnici e analitici</strong>
                    </p>
                    <p style="font-size: 0.8rem; color: #6b5d4f; margin: 0; line-height: 1.4;">
                        Utilizziamo cookie tecnici necessari al funzionamento e, con il tuo consenso, Google Analytics 4 per statistiche anonime di navigazione.
                        <a href="/cookie-policy" style="color: #8B4513; text-decoration: underline;">Maggiori informazioni</a>
                    </p>
                </div>
                <div style="display: flex; gap: 0.8rem; flex-wrap: wrap;">
                    <button onclick="acceptCookies()" style="
                        padding: 0.7rem 1.5rem;
                        background: linear-gradient(135deg, #8B4513, #A0522D);
                        color: white;
                        border: none;
                        border-radius: 50px;
                        font-size: 0.85rem;
                        cursor: pointer;
                        font-family: inherit;
                    ">Accetta</button>
                    <button onclick="rejectCookies()" style="
                        padding: 0.7rem 1.5rem;
                        background: transparent;
                        color: #8B4513;
                        border: 1px solid #8B4513;
                        border-radius: 50px;
                        font-size: 0.85rem;
                        cursor: pointer;
                        font-family: inherit;
                    ">Rifiuta</button>
                    <button onclick="openCookieSettings()" style="
                        padding: 0.7rem 1.5rem;
                        background: transparent;
                        color: #6b5d4f;
                        border: 1px solid #ccc;
                        border-radius: 50px;
                        font-size: 0.85rem;
                        cursor: pointer;
                        font-family: inherit;
                    ">Personalizza</button>
                </div>
            </div>
        </div>
    </div>

    <!-- Modal Personalizzazione -->
    <div id="cookie-modal" style="
        display: none;
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0,0,0,0.5);
        z-index: 10000;
        padding: 1rem;
        overflow-y: auto;
    ">
        <div style="
            background: #fff;
            max-width: 500px;
            margin: 2rem auto;
            border-radius: 12px;
            overflow: hidden;
            font-family: 'Inter', -apple-system, sans-serif;
        ">
            <div style="background: linear-gradient(135deg, #8B4513, #B8860B); color: white; padding: 1.2rem;">
                <h3 style="margin: 0; font-size: 1.2rem;">Preferenze Cookie</h3>
            </div>
            <div style="padding: 1.5rem;">

                <!-- Cookie Tecnici -->
                <div style="margin-bottom: 1.5rem; padding-bottom: 1rem; border-bottom: 1px solid #eee;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                        <strong style="color: #8B4513;">Cookie Tecnici</strong>
                        <span style="background: #8B4513; color: white; padding: 0.2rem 0.6rem; border-radius: 10px; font-size: 0.75rem;">Sempre attivi</span>
                    </div>
                    <p style="font-size: 0.85rem; color: #6b5d4f; margin: 0; line-height: 1.5;">
                        Necessari per il funzionamento del sito: memorizzazione delle preferenze cookie, protezione sicurezza Cloudflare.
                    </p>
                </div>

                <!-- Cookie Analitici -->
                <div style="margin-bottom: 1.5rem; padding-bottom: 1rem; border-bottom: 1px solid #eee;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                        <strong style="color: #555;">Cookie Analitici</strong>
                        <span id="analyticsStatusBadge" style="background: #ccc; color: #666; padding: 0.2rem 0.6rem; border-radius: 10px; font-size: 0.75rem;">Richiedono consenso</span>
                    </div>
                    <p style="font-size: 0.85rem; color: #6b5d4f; margin: 0; line-height: 1.5;">
                        <strong>Google Analytics 4</strong> — statistiche anonime di navigazione (pagine visitate, durata sessione, provenienza del traffico). Cookie: <code>_ga</code> (2 anni), <code>_ga_*</code> (1 giorno). Attivati solo con il tuo consenso.
                    </p>
                </div>

                <!-- Cloudflare Web Analytics (no cookie) -->
                <div style="margin-bottom: 1.5rem; padding-bottom: 1rem; border-bottom: 1px solid #eee;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                        <strong style="color: #8B4513;">Cloudflare Web Analytics</strong>
                        <span style="background: #8B4513; color: white; padding: 0.2rem 0.6rem; border-radius: 10px; font-size: 0.75rem;">Sempre attivi</span>
                    </div>
                    <p style="font-size: 0.85rem; color: #6b5d4f; margin: 0; line-height: 1.5;">
                        Statistiche aggregate <strong>senza cookie</strong>, senza tracciamento individuale, senza raccolta di dati personali. Conforme GDPR senza consenso (Privacy-First Analytics).
                    </p>
                </div>

                <!-- Cookie Marketing -->
                <div style="margin-bottom: 1.5rem;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                        <strong style="color: #aaa;">Cookie Marketing</strong>
                        <span style="background: #eee; color: #aaa; padding: 0.2rem 0.6rem; border-radius: 10px; font-size: 0.75rem;">Non utilizzati</span>
                    </div>
                    <p style="font-size: 0.85rem; color: #aaa; margin: 0; line-height: 1.5;">
                        Questo sito non utilizza cookie pubblicitari o di profilazione.
                    </p>
                </div>

                <div style="display: flex; gap: 0.8rem; justify-content: flex-end; margin-top: 1.5rem;">
                    <button onclick="rejectCookies()" style="
                        padding: 0.7rem 1.2rem;
                        background: transparent;
                        color: #8B4513;
                        border: 1px solid #8B4513;
                        border-radius: 50px;
                        font-size: 0.85rem;
                        cursor: pointer;
                        font-family: inherit;
                    ">Rifiuta analitici</button>
                    <button onclick="acceptCookies()" style="
                        padding: 0.7rem 1.2rem;
                        background: linear-gradient(135deg, #8B4513, #A0522D);
                        color: white;
                        border: none;
                        border-radius: 50px;
                        font-size: 0.85rem;
                        cursor: pointer;
                        font-family: inherit;
                    ">Accetta tutti</button>
                </div>
            </div>
        </div>
    </div>
    `;

    document.body.insertAdjacentHTML('beforeend', bannerHTML);
})();

// ─── Funzioni globali ────────────────────────────────────────────────────────

function acceptCookies() {
    localStorage.setItem('cookieConsent', 'accepted');
    localStorage.setItem('cookieConsentDate', new Date().toISOString());
    // Attiva GA4
    gtag('consent', 'update', { 'analytics_storage': 'granted' });
    hideBanner();
}

function rejectCookies() {
    localStorage.setItem('cookieConsent', 'rejected');
    localStorage.setItem('cookieConsentDate', new Date().toISOString());
    // GA4 rimane denied (già impostato di default)
    hideBanner();
}

function openCookieSettings() {
    const modal = document.getElementById('cookie-modal');
    if (modal) modal.style.display = 'block';
}

function hideBanner() {
    const banner = document.getElementById('cookie-banner');
    const modal = document.getElementById('cookie-modal');
    if (banner) banner.style.display = 'none';
    if (modal) modal.style.display = 'none';
}

// Chiudi modal cliccando fuori
document.addEventListener('click', function (e) {
    const modal = document.getElementById('cookie-modal');
    if (modal && e.target === modal) {
        modal.style.display = 'none';
    }
});
