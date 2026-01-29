# Calendario Yorùbá

Calendario tradizionale Yorùbá con settimana di 4 giorni dedicati agli Òrìṣà.

**Autore:** Lorenzo Okìkí Rossi - Casa Obàtálá

---

## Struttura File

```
calendario-yoruba/
├── index.html          # App principale
├── service-worker.js   # Per funzionalità offline
├── manifest.json       # Configurazione PWA
├── logo.png            # Logo 192x192 (da aggiungere)
├── logo-512.png        # Logo 512x512 (da aggiungere)
└── logo-placeholder.svg # Logo temporaneo
```

---

## Istruzioni per il Logo

1. Quando avrai il logo definitivo, salvalo in due dimensioni:
   - `logo.png` → 192x192 pixel
   - `logo-512.png` → 512x512 pixel

2. Puoi convertire il logo da SVG a PNG usando:
   - [CloudConvert](https://cloudconvert.com/svg-to-png)
   - [Convertio](https://convertio.co/it/svg-png/)

---

## Deployment su casaobatala.it

### Opzione 1: Sottocartella (consigliato)
Carica tutti i file in: `casaobatala.it/calendario/`

L'app sarà accessibile a: `https://casaobatala.it/calendario/`

### Opzione 2: Sottodominio
Configura un sottodominio: `calendario.casaobatala.it`

---

## Generare APK per Android

### Metodo 1: PWA Builder (più semplice)

1. Carica l'app online (es. `casaobatala.it/calendario/`)
2. Vai su [PWABuilder.com](https://www.pwabuilder.com/)
3. Inserisci l'URL della tua app
4. Clicca "Start" → "Package for stores"
5. Seleziona "Android"
6. Scarica l'APK generato

### Metodo 2: Bubblewrap (più controllo)

Se hai Node.js installato:

```bash
npm install -g @anthropic/anthropic-sdk
npx @anthropic/anthropic-sdk init
npx @anthropic/anthropic-sdk build
```

---

## Funzionalità dell'App

### Calendario
- ✅ Settimana Yorùbá di 4 giorni (Ọ̀sẹ̀)
- ✅ Anno Yorùbá calcolato automaticamente
- ✅ Evidenziazione del giorno corrente
- ✅ Navigazione mese/anno
- ✅ Pulsante "Torna a oggi"

### Giorni Speciali
- 🟢 **Ọjọ́ Nla Obàtálá** - Grande giorno di Obàtálá
- 🟡 **Ìtàdógún** - Ogni 16 giorni
- 🔴 **Jàkúta Olóyìn** - Ogni 28 giorni
- 🟣 **Festività** - Capodanno Yorùbá (3 giugno)

### I 4 Giorni della Settimana Yorùbá

| Giorno | Òrìṣà Principali |
|--------|------------------|
| Ọsẹ́ Ọ̀sà | Obàtálá, Ẹgúngún, Ìyáàmi, Yemọja |
| Ọsẹ́ Ifá | Ifá, Odù, Ajé, Ọ̀ṣun, Èṣù |
| Ọsẹ́ Ògún | Ògún, Ọ̀sọ́ọ̀sì, Òkò, Erinlẹ̀ |
| Ọsẹ́ Jàkúta | Ṣàngó, Ọya, Àgànjù, Ọbalúayé |

### PWA
- ✅ Installabile su dispositivi
- ✅ Funziona offline
- ✅ Notifiche giornaliere (con permesso)

---

## Personalizzazioni

### Modificare i colori
Nel file `index.html`, cerca la sezione `<style>` e modifica:
- `#8B4513` → Marrone primario
- `#B8860B` → Oro secondario
- `#fafafa` → Sfondo chiaro

### Aggiungere festività
Cerca l'oggetto `festivita` nel JavaScript:

```javascript
const festivita = {
    5: {  // Giugno (mese 5, zero-indexed)
        2: { nome: 'FINE ANNO' }, 
        3: { nome: 'CAPODANNO' }
    },
    // Aggiungi altre festività qui
    11: {  // Dicembre
        25: { nome: 'NATALE' }
    }
};
```

---

## Supporto

Per domande o supporto:
- 📧 lorenzo.okiki@gmail.com
- 🌐 casaobatala.it

---

© 2025 Casa Obàtálá - Lorenzo Okìkí Rossi
