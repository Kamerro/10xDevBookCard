# UI Diagram

```mermaid
flowchart TD
  U[User] -->|Opens app| UI[UI Shell]
  UI --> NAV[Navigation]
  UI --> PAGE[Page Content]

  NAV -->|Selects| SEARCH[Search View]
  NAV -->|Selects| LIBRARY[Library View]
  NAV -->|Selects| SETTINGS[Settings View]

  SEARCH -->|Query| RESULTS[Results List]
  RESULTS -->|Open item| DETAIL[Card Detail]

  LIBRARY -->|Browse| COLLECTION[Collection List]
  COLLECTION -->|Open item| DETAIL

  DETAIL -->|Action| EDIT[Edit Card]
  EDIT -->|Save| DETAIL

  SETTINGS -->|Update preferences| UI
```
