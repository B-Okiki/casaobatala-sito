// Cookie Banner per Casa Obàtálá
// Conforme GDPR - Solo cookie tecnici

(function() {
    // Controlla se l'utente ha già fatto una scelta
    if (localStorage.getItem('cookieConsent')) {
        return; // Non mostrare il banner se già accettato/rifiutato
    }

    // Crea il banner
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
                        <strong style="color: #8B4513;">🍪 Questo sito usa cookie tecnici</strong>
                    </p>
                    <p style="font-size: 0.8rem; color: #6b5d4f; margin: 0; line-height: 1.4;">
                        Utilizziamo solo cookie tecnici necessari al funzionamento del sito. Non usiamo cookie di profilazione o tracciamento.
                        <a href="cookie-policy.html" style="color: #8B4513; text-decoration: underline;">Maggiori informazioni</a>
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
                <div style="margin-bottom: 1.5rem; padding-bottom: 1rem; border-bottom: 1px solid #eee;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                        <strong style="color: #8B4513;">Cookie Tecnici</strong>
                        <span style="background: #8B4513; color: white; padding: 0.2rem 0.6rem; border-radius: 10px; font-size: 0.75rem;">Sempre attivi</span>
                    </div>
                    <p style="font-size: 0.85rem; color: #6b5d4f; margin: 0; line-height: 1.5;">
                        Necessari per il funzionamento del sito. Includono la memorizzazione delle tue preferenze sui cookie e i cookie di sicurezza del server.
                    </p>
                </div>
                <div style="margin-bottom: 1.5rem; padding-bottom: 1rem; border-bottom: 1px solid #eee;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                        <strong style="color: #666;">Cookie Analitici</strong>
                        <span style="background: #ccc; color: #666; padding: 0.2rem 0.6rem; border-radius: 10px; font-size: 0.75rem;">Non utilizzati</span>
                    </div>
                    <p style="font-size: 0.85rem; color: #6b5d4f; margin: 0; line-height: 1.5;">
                        Questo sito non utilizza cookie analitici o di tracciamento.
                    </p>
                </div>
                <div style="margin-bottom: 1.5rem;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                        <strong style="color: #666;">Cookie di Marketing</strong>
                        <span style="background: #ccc; color: #666; padding: 0.2rem 0.6rem; border-radius: 10px; font-size: 0.75rem;">Non utilizzati</span>
                    </div>
                    <p style="font-size: 0.85rem; color: #6b5d4f; margin: 0; line-height: 1.5;">
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
                    ">Rifiuta tutti</button>
                    <button onclick="acceptCookies()" style="
                        padding: 0.7rem 1.2rem;
                        background: linear-gradient(135deg, #8B4513, #A0522D);
                        color: white;
                        border: none;
                        border-radius: 50px;
                        font-size: 0.85rem;
                        cursor: pointer;
                    ">Accetta tutti</button>
                </div>
            </div>
        </div>
    </div>
    `;

    // Inserisci il banner nel DOM
    document.body.insertAdjacentHTML('beforeend', bannerHTML);
})();

// Funzioni globali
function acceptCookies() {
    localStorage.setItem('cookieConsent', 'accepted');
    localStorage.setItem('cookieConsentDate', new Date().toISOString());
    hideBanner();
}

function rejectCookies() {
    localStorage.setItem('cookieConsent', 'rejected');
    localStorage.setItem('cookieConsentDate', new Date().toISOString());
    hideBanner();
}

function openCookieSettings() {
    document.getElementById('cookie-modal').style.display = 'block';
}

function hideBanner() {
    const banner = document.getElementById('cookie-banner');
    const modal = document.getElementById('cookie-modal');
    if (banner) banner.style.display = 'none';
    if (modal) modal.style.display = 'none';
}

// Chiudi modal cliccando fuori
document.addEventListener('click', function(e) {
    const modal = document.getElementById('cookie-modal');
    if (e.target === modal) {
        modal.style.display = 'none';
    }
});
