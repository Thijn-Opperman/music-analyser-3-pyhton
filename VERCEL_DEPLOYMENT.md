# 🚀 Vercel Deployment Gids

Deze gids legt uit hoe je dit Python Flask project op Vercel kunt deployen.

## 📋 Vereisten

1. Een Vercel account (gratis op [vercel.com](https://vercel.com))
2. Vercel CLI geïnstalleerd (optioneel, kan ook via web interface)
3. Git repository (GitHub, GitLab, of Bitbucket)

## 🔧 Stap 1: Vercel CLI Installeren (Optioneel)

Als je via de command line wilt deployen:

```bash
npm install -g vercel
```

Of gebruik de web interface op vercel.com (aanbevolen voor beginners).

## 📤 Stap 2: Project Deployen

### Optie A: Via Vercel Web Interface (Aanbevolen)

1. **Ga naar [vercel.com](https://vercel.com)** en log in
2. **Klik op "Add New Project"**
3. **Import je Git repository** (verbind GitHub/GitLab/Bitbucket)
4. **Configureer het project:**
   - **Framework Preset**: Laat leeg of kies "Other"
   - **Root Directory**: `.` (laat leeg)
   - **Build Command**: Laat leeg (niet nodig voor Python)
   - **Output Directory**: Laat leeg
   - **Install Command**: `pip install -r requirements.txt`
5. **Klik op "Deploy"**

### Optie B: Via Command Line

```bash
# In de project directory
cd /Users/thijnopperman/Documents/GitHub/music-analyser-3-pyhton

# Login bij Vercel (eerste keer)
vercel login

# Deploy
vercel

# Volg de instructies op het scherm
```

## ⚙️ Belangrijke Configuratie

Het project bevat al de volgende bestanden voor Vercel:

- ✅ `vercel.json` - Vercel configuratie
- ✅ `api/index.py` - Serverless function wrapper
- ✅ `.vercelignore` - Bestanden die niet geüpload hoeven te worden

## ⚠️ Belangrijke Opmerkingen

### ⚠️ KRITIEK: Serverless Function Size Limiet

**PROBLEEM**: Vercel heeft een limiet van **250 MB unzipped** voor serverless functions. 

De dependencies (`librosa`, `scipy`, `numpy`, `matplotlib`) zijn zeer groot en kunnen deze limiet overschrijden.

**OPLOSSINGEN**:

1. **Verwijder grote bestanden uit repository**:
   ```bash
   # Zorg dat uploads/ en static/analysis_images/ niet in git staan
   git rm -r --cached uploads/* static/analysis_images/*
   git commit -m "Remove large files"
   ```

2. **Gebruik .vercelignore** (al aangemaakt):
   - Zorg dat grote bestanden uitgesloten worden
   - Check dat `.vercelignore` de juiste folders bevat

3. **Alternatieve Deployment Platforms** (aanbevolen voor deze app):
   - **Railway.app** - Geen size limiet, gratis tier beschikbaar
   - **Render.com** - Goede Python support, gratis tier
   - **Fly.io** - Goede voor serverless Python apps
   - **Heroku** - Klassieke optie (betaald)

4. **Als je toch Vercel wilt gebruiken**:
   - Upgrade naar **Pro tier** (heeft hogere limieten)
   - Overweeg om audio processing naar een externe service te verplaatsen
   - Gebruik een lichtere audio library (maar dit vereist code aanpassingen)

### 1. Timeout Limieten
- **Free tier**: 10 seconden timeout per request
- **Pro tier**: 60 seconden timeout
- Audio analyse kan lang duren! Overweeg Pro tier voor langere tracks.

### 2. Bestandsopslag
- Bestanden worden tijdelijk opgeslagen in `/tmp` (ephemeral)
- Bestanden worden **niet** permanent opgeslagen tussen requests
- Elke analyse is stateless

### 3. Memory Limieten
- Free tier: 1024 MB
- Pro tier: 3008 MB
- Audio analyse kan veel geheugen gebruiken

### 4. Dependencies
Zorg dat alle dependencies in `requirements.txt` staan. Vercel installeert deze automatisch.

## 🔍 Testen na Deployment

Na deployment krijg je een URL zoals: `https://jouw-project.vercel.app`

Test de volgende endpoints:
- `/` - Hoofdpagina
- `/upload` - File upload endpoint (POST)

## 🐛 Troubleshooting

### Probleem: "Module not found"
- **Oplossing**: Controleer of alle dependencies in `requirements.txt` staan

### Probleem: "Timeout"
- **Oplossing**: 
  - Upgrade naar Pro tier voor 60 seconden timeout
  - Of optimaliseer je audio analyse code

### Probleem: "Function too large"
- **Oplossing**: 
  - Controleer `.vercelignore` om onnodige bestanden uit te sluiten
  - Verwijder grote test bestanden uit de repository

### Probleem: "Static files not loading"
- **Oplossing**: 
  - Zorg dat `static/` folder in de repository staat
  - Check `vercel.json` routes configuratie

## 📝 Environment Variables (Optioneel)

Als je environment variables nodig hebt:

1. Ga naar je project op Vercel dashboard
2. Settings → Environment Variables
3. Voeg variabelen toe zoals `VERCEL=1` (al automatisch gezet)

## 🔄 Updates Deployen

Na elke `git push` naar je main branch, deployt Vercel automatisch een nieuwe versie.

Of handmatig:
```bash
vercel --prod
```

## 📚 Meer Informatie

- [Vercel Python Documentation](https://vercel.com/docs/concepts/functions/serverless-functions/runtimes/python)
- [Vercel CLI Documentation](https://vercel.com/docs/cli)

## ✅ Checklist voor Deployment

- [ ] Git repository is verbonden met Vercel
- [ ] `vercel.json` bestaat en is correct
- [ ] `api/index.py` bestaat
- [ ] `requirements.txt` bevat alle dependencies
- [ ] `.vercelignore` sluit onnodige bestanden uit
- [ ] Test lokaal met `python app.py` (optioneel)
- [ ] Deploy via Vercel dashboard of CLI
- [ ] Test de deployed versie

---

**Succes met je deployment! 🎉**

