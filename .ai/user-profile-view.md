# User Profile View Specification

## 📋 Przegląd
Widok profilu użytkownika w BookCards - interfejs do zarządzania podstawowymi ustawieniami konta i preferencjami wizualnymi.

---

## 🎯 Komponenty Widoku

### 1. **Sekcja Podstawowych Danych**
```
┌─────────────────────────────────────┐
│  [AVATAR]  [EMAIL]                  │
│             [NAZWA UŻYTKOWNIKA]      │
│                                     │
│  [Edytuj profil]                    │
└─────────────────────────────────────┘
```

**Pola:**
- **Avatar** (upload/change)
- **Email** (tylko do odczytu)
- **Nazwa użytkownika** (edytowalna)
- **Przycisk "Edytuj profil"**

---

### 2. **Preferencje Wizualne**
```
┌─────────────────────────────────────┐
│  🎨 Wygląd                          │
│                                     │
│  Motyw: [ Dark ▼ ]                 │
│  Czcionka: [ Inter ▼ ]             │
│  Rozmiar tekstu: [ Medium ▼ ]       │
│                                     │
│  [Podgląd]                          │
└─────────────────────────────────────┘
```

**Opcje:**
- **Motyw:** Dark, Light, Auto
- **Czcionka:** Inter, Roboto, System UI
- **Rozmiar tekstu:** Small, Medium, Large

---

### 3. **Ustawienia AI**
```
┌─────────────────────────────────────┐
│  🤖 Ustawienia AI                   │
│                                     │
│  Model: [ GPT-4o-mini ▼ ]          │
│  Kreatywność: [ 50% ]               │
│  ┌─────────────────────────────────┐ │
│  │ Konserwatywny ●────● Kreatywny │ │
│  └─────────────────────────────────┘ │
└─────────────────────────────────────┘
```

**Opcje:**
- **Model:** GPT-4o-mini, GPT-4o, Claude-3-haiku
- **Kreatywność:** Slider 0-100 (temperature)

---

### 4. **Bezpieczeństwo**
```
┌─────────────────────────────────────┐
│  🔒 Bezpieczeństwo                  │
│                                     │
│  [ Zmień hasło ]                    │
│  [ Usuń konto ]                    │
└─────────────────────────────────────┘
```

**Przyciski:**
- **Zmień hasło** -> modal/popup
- **Usuń konto** -> potwierdzenie z ostrzeżeniem

---

### 5. **Język i Region**
```
┌─────────────────────────────────────┐
│  🌍 Język                           │
│                                     │
│  Język interfejsu: [ Polski ▼ ]    │
│                                     │
│  [Zapisz zmiany]                   │
└─────────────────────────────────────┘
```

**Opcje:**
- **Język:** Polski, English

---

### 6. **Plan Pro**
```
┌─────────────────────────────────────┐
│  ⭐ Plan Pro                        │
│                                     │
│  Aktualny plan: Free                │
│                                     │
│  📚 4 książki                       │
│  📝 5 notatek na książkę            │
│                                     │
│  [ Become Pro -> Learn more! ]     │
└─────────────────────────────────────┘
```

**Funkcje:**
- Status planu
- Limity użytkownika
- CTA do upgrade

---

## 🎨 Design System

### Kolory
- **Background:** `var(--dark-gray)`
- **Karty:** `var(--darker-gray)`
- **Akcenty:** `var(--gold)`
- **Tekst:** `var(--text-light)`
- **Border:** `rgba(156, 163, 175, 0.3)`

### Layout
- **Grid:** 2-kolumnowy (desktop) / 1-kolumnowy (mobile)
- **Spacing:** 16px między sekcjami
- **Border radius:** 12px
- **Padding:** 20px wewnątrz sekcji

### Interakcje
- **Hover:** `rgba(251, 191, 36, 0.1)` background
- **Focus:** `var(--ambient-blue)` outline
- **Transitions:** `0.3s ease`

---

## 📱 Responsywność

### Desktop (>768px)
```
┌─────────────┬─────────────┐
│   Avatar    │   Ustawienia│
│   + Dane    │   wizualne  │
│             │             │
│   AI        │   Język     │
│   + Bezpiec │             │
│   ────────  │   Plan Pro  │
└─────────────┴─────────────┘
```

### Mobile (<768px)
```
┌─────────────────────────────┐
│        Avatar + Dane        │
├─────────────────────────────┤
│      Ustawienia wizualne    │
├─────────────────────────────┤
│         Ustawienia AI       │
├─────────────────────────────┤
│        Bezpieczeństwo        │
├─────────────────────────────┤
│          Język              │
├─────────────────────────────┤
│          Plan Pro           │
└─────────────────────────────┘
```

---

## 🔄 Flow Użytkownika

### 1. **Wejście do profilu**
- URL: `/profile`
- Dostęp z dashboarda (avatar/user menu)

### 2. **Edycja danych**
- Click "Edytuj profil" -> inline editing
- Auto-save po zmianie

### 3. **Zmiana preferencji**
- Real-time preview dla motywu/czcionki
- Slider dla kreatywności AI
- Dropdown dla modelu

### 4. **Bezpieczeństwo**
- Modal dla zmiany hasła
- Confirmation dialog dla delete account

### 5. **Upgrade Pro**
- Click "Become Pro" -> redirect do pricing page
- Lub inline upgrade modal

---

## 🛠️ Techniczne Wymagania

### Frontend
- **Framework:** React/Vue (zgodnie z stackiem)
- **State management:** local state + API calls
- **Form validation:** client + server side

### Backend
- **API endpoints:** `/api/user/profile`
- **Database:** user_settings table
- **File upload:** avatar storage

### Integracje
- **AI providers:** OpenRouter API
- **Storage:** S3/Cloudinary dla avatarów

---

## 📋 Checklist Implementacji

### MVP Features
- [ ] Podstawowe dane (avatar, nazwa)
- [ ] Motyw kolorystyczny
- [ ] Ustawienia AI (model, kreatywność)
- [ ] Zmiana hasła
- [ ] Język interfejsu
- [ ] Plan Pro sekcja

### Future Features
- [ ] Czcionka i rozmiar tekstu
- [ ] Delete account
- [ ] Real-time preview
- [ ] Advanced AI settings

---

## 🎯 Success Metrics

- **Engagement:** Czas spędzony w profilu
- **Conversion:** Pro upgrade rate
- **Retention:** Users changing settings
- **Satisfaction:** Feedback na nowy design

---

*Created: 2026-02-01*
*Version: 1.0*
*Status: Planning*
