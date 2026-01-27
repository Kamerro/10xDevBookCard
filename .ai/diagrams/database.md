# Database Diagram

```mermaid
UserDiagram
  USER {
    string id
    string email
    string name
    datetime created_at
  }

  BOOK {
    string id
    string title
    string author
    datetime created_at
  }

  CARD {
    string id
    string book_id
    string user_id
    string front
    string back
    datetime created_at
    datetime updated_at
  }

  TAG {
    string id
    string user_id
    string name
  }

  CARD_TAG {
    string card_id
    string tag_id
  }

  COLLECTION {
    string id
    string user_id
    string name
    datetime created_at
  }

  COLLECTION_CARD {
    string collection_id
    string card_id
  }

  USER ||--o{ BOOK : owns
  USER ||--o{ CARD : creates
  BOOK ||--o{ CARD : contains

  USER ||--o{ TAG : defines
  CARD ||--o{ CARD_TAG : has
  TAG ||--o{ CARD_TAG : labels

  USER ||--o{ COLLECTION : owns
  COLLECTION ||--o{ COLLECTION_CARD : contains
  CARD ||--o{ COLLECTION_CARD : included_in
```
