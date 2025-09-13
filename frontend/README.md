# W3 Manifest Management System - Frontend

Un'applicazione web moderna per la gestione dei manifest e degli ordini, sviluppata con Next.js, React, TypeScript e Tailwind CSS.

## 🚀 Caratteristiche Principali

### ✨ **UI/UX Moderna**
- **Design System** completo con Tailwind CSS
- **Componenti riusabili** (Button, Input, Card, etc.)
- **Layout responsive** per desktop, tablet e mobile
- **Sidebar collassabile** e **navbar responsive**
- **Animazioni smooth** e transizioni fluide

### 🔐 **Sistema di Autenticazione**
- **JWT Authentication** con refresh token
- **Role-based access** (Operator/Admin)
- **Protezione automatica** delle route
- **Context API** per gestione stato globale
- **Login/Logout** sicuro con cookie HTTP-only

### 📊 **Dashboard Interattiva**
- **Statistiche in tempo reale** su ordini e manifest
- **Quick actions** per operazioni frequenti
- **Cards informative** con metriche chiave
- **Test API integration** integrato

### 📋 **Gestione Ordini**
- **Lista paginata** con filtri avanzati
- **Ricerca full-text** per service ID e descrizione
- **Filtri per stato**, data, priorità
- **Visualizzazione dettagliata** di ogni ordine
- **Badge colorati** per stati e priorità

### 📄 **Upload e Parsing Manifest**
- **Drag & drop** per upload file .docx/.doc
- **Processing in tempo reale** con feedback visivo
- **Preview dei servizi** estratti
- **Gestione errori** e validazione
- **Creazione batch** ordini da manifest

### 📈 **Analytics e Reportistica**
- **Metriche chiave** visualizzate con grafici
- **Trend mensili** e giornalieri
- **Tassi di completamento** e processing
- **Distribuzione stati** per ordini e manifest

## 🛠 **Stack Tecnologico**

### **Frontend**
- **Next.js 14** - Framework React con SSR/SSG
- **React 18** - Libreria UI con hooks moderni
- **TypeScript 5** - Tipizzazione statica
- **Tailwind CSS 3** - Framework CSS utility-first
- **Axios** - Client HTTP per API calls

### **State Management**
- **React Context** - Gestione stato autenticazione
- **React Hooks** - Status locale componenti
- **Cookie management** - Persistenza token JWT

### **Utilità e Strumenti**
- **clsx + tailwind-merge** - Gestione classi CSS condizionali
- **react-dropzone** - Drag & drop file upload
- **js-cookie** - Gestione cookie lato client

## 🏗 **Architettura Implementata**

```
frontend/
├── app/                    # Next.js 13+ App Router
│   ├── dashboard/         # Dashboard principale ✅
│   ├── login/            # Autenticazione ✅
│   ├── register/         # Registrazione utenti ✅
│   ├── orders/           # Gestione ordini ✅
│   ├── manifests/        # Cronologia manifest ✅
│   ├── upload/           # Upload manifest ✅
│   ├── analytics/        # Reportistica ✅
│   └── globals.css       # Stili globali ✅
├── components/
│   ├── ui/               # Componenti UI riusabili ✅
│   ├── layout/           # Layout e navigazione ✅
│   └── test/            # Componenti di testing ✅
├── context/              # React Context providers ✅
├── services/            # API client e servizi ✅
├── types/               # Definizioni TypeScript ✅
└── utils/               # Utilità e helper ✅
```

## 🚀 **Come Iniziare**

### **Prerequisiti**
- Node.js 18+ e npm
- Backend Flask attivo su porta 5000

### **Installazione e Avvio**

```bash
# Naviga nella cartella frontend
cd frontend

# Installa le dipendenze
npm install

# Avvia in modalità development
npm run dev
```

### **URL di Accesso**
- **Frontend**: http://localhost:3001
- **Backend API**: http://127.0.0.1:5000/api

## 🎯 **Status Implementazione**

- ✅ **Setup progetto** Next.js + TypeScript + Tailwind
- ✅ **Sistema autenticazione** JWT con Context API
- ✅ **Layout responsive** con Sidebar e Navbar
- ✅ **Componenti UI** riusabili (Button, Input, Card)
- ✅ **Dashboard** con statistiche e quick actions
- ✅ **Pagina Orders** con filtri e paginazione
- ✅ **Upload Manifest** con drag & drop
- ✅ **Analytics** con metriche e trend
- ✅ **API Integration** completa con error handling
- ✅ **Test Component** per debugging API

## 🎨 **Design System**

### **Colori Primari**
- **Blue**: `#3B82F6` (Primary actions)
- **Green**: `#22C55E` (Success states)  
- **Yellow**: `#F59E0B` (Warning states)
- **Red**: `#EF4444` (Error/Danger states)
- **Gray**: Scala completa per testi e backgrounds

### **Componenti Implementati**

#### **Button**
```tsx
<Button 
  variant="primary|secondary|outline|ghost|danger"
  size="sm|md|lg"
  isLoading={boolean}
>
  Click me
</Button>
```

#### **Input**
```tsx
<Input 
  label="Email"
  error="Campo obbligatorio"
  helperText="Inserisci una email valida"
/>
```

#### **Card**
```tsx
<Card hover>
  <CardHeader>Titolo</CardHeader>
  <CardContent>Contenuto</CardContent>
  <CardFooter>Azioni</CardFooter>
</Card>
```

---

**✨ Sviluppato con ❤️ utilizzando Next.js, React, TypeScript e Tailwind CSS**
