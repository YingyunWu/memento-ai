# Memento AI

> A multimodal AI-powered digital journaling system that turns fragmented daily memories into meaningful, structured, and eventually AI-generated journals.

Memento AI is a personal memory and digital journaling project built around a simple idea:

**A day is rarely remembered as one complete story. It is remembered through fragments — a thought, a photo, a song, a video, or a small moment.**

Memento AI allows users to continuously collect these fragments throughout the day and organize them into a journal based on each date.

The long-term goal is to use AI to understand these multimodal memories and automatically transform them into a personalized digital journal.

---

## ✨ Core Concept

```text
                 Memento AI

          Fragmented Daily Memories
                     │
       ┌─────────────┼─────────────┐
       │             │             │
      Text         Photo         Music
       │             │             │
       └─────────────┼─────────────┘
                     │
                   Video
                     │
                     ▼
              Memory System
                     │
                     ▼
              AI Understanding
                     │
                     ▼
            Journal Generation
                     │
                     ▼
          Personalized Daily Journal
```

Memento AI is designed around **day-level journaling**.

Each date represents one journal, and each journal can contain multiple memories.

Users can continue adding new memories to a previous date and modify existing memories whenever they want.

---

## 🚀 Current Features

### 📅 Daily Journals

Memories are organized by date.

For example:

```text
2026-08-25
│
├── Text Memory
├── Text Memory
├── Photo Memory
├── Music Memory
└── Video Memory
```

Users can add new memories to previous days instead of being restricted to the current date.

### 🧠 Multimodal Memories

Memento AI supports four types of memories:

| Type | Description |
|---|---|
| 📝 Text | Thoughts, notes, reflections, events |
| 📷 Photo | Local photos associated with a journal |
| 🎵 Music | Music links associated with a memory |
| 🎬 Video | Video links associated with a memory |

This structure is designed to support future multimodal AI processing.

### ✏️ Editable Memories

Memories are not treated as immutable diary entries.

Users can:

- Create memories
- View memories
- Edit memories
- Delete memories
- Add new memories to previous dates

This allows a journal to evolve over time.

For example:

```text
August 25
    ↓
Initial thought
    ↓
Add a photo later
    ↓
Add a song later
    ↓
Edit the original thought
    ↓
AI generates the final journal
```

### 💾 Persistent Storage

Memento AI currently uses SQLite for persistent local storage.

The database records information such as:

```text
Journal
├── Date
│
└── Memories
    ├── ID
    ├── Type
    ├── Content
    ├── Created At
    └── Updated At
```

This allows memories to remain available across multiple program sessions.

### 📷 Local Media Storage

Uploaded photos are stored locally in date-based folders:

```text
data/
└── media/
    └── YYYY-MM-DD/
        ├── photo1.jpg
        ├── photo2.jpg
        └── ...
```

The database stores the corresponding file path.

Personal media is excluded from Git version control.

---

## 🧠 AI Roadmap

The current version focuses on building a reliable memory and data foundation.

The next stage is to introduce AI capabilities.

### 1. AI Journal Generation

The core AI goal is to transform fragmented memories into a coherent daily journal.

```text
Text + Photos + Music + Video
              │
              ▼
        Multimodal AI
              │
              ▼
       Context Understanding
              │
              ▼
        Journal Generation
```

### 2. Automatic Summarization

Memento AI will summarize multiple fragmented memories while preserving important details and context.

### 3. Mood and Theme Detection

The system may identify:

- Mood
- Themes
- Important events
- Activities
- Recurring topics

These signals can be used to improve journal generation.

### 4. Multimodal Understanding

Future versions will combine information from different media types.

For example:

```text
Text:
"今天去了海边。"

Photo:
A sunset over the ocean

Music:
A calm instrumental track

        ↓

AI Understanding

        ↓

A richer description of the day
```

The goal is to generate a journal that reflects the combination of these memories rather than processing each item independently.

### 5. Personalized Writing Style

Users will eventually be able to choose different journal styles, such as:

- Minimalist
- Casual
- Literary
- Reflective
- Travel diary
- Photo journal

The system may also learn from previous journal entries to better match the user's preferred writing style.

---

## 🏗️ Current Architecture

The current prototype uses a simple Python and SQLite architecture:

```text
User
 │
 ▼
CLI Interface
 │
 ▼
Python Application
 │
 ├── Journal Management
 ├── Memory Management
 └── Media Handling
 │
 ▼
SQLite Database
```

The architecture is intentionally simple at the current stage so that the core data model can be developed and tested first.

The planned architecture will evolve toward:

```text
User Interface
       │
       ▼
Application Layer
       │
       ├── Journal Service
       ├── Memory Service
       └── Media Service
       │
       ▼
AI Layer
       │
       ├── LLM
       ├── Multimodal Understanding
       ├── Summarization
       └── Journal Generation
       │
       ▼
Data Layer
       │
       ├── SQLite
       └── Local Media Storage
```

---

## 🛠️ Tech Stack

### Current

- Python
- SQLite
- Git
- GitHub
- PyCharm

### Planned

- Streamlit or another lightweight web framework
- LLM APIs
- Structured outputs
- Multimodal AI
- Embeddings
- Semantic similarity
- Information retrieval
- Data visualization

---

## 📂 Project Structure

Current prototype:

```text
memento-ai/
│
├── main.py
├── database.py
├── README.md
├── LICENSE
├── .gitignore
│
├── data/
│   └── media/
│
└── memento.db
```

The local database and personal media are excluded from version control.

---

## 🔐 Privacy

Memento AI is designed to handle personal memories.

Personal diary data, uploaded media, local databases, and API credentials should not be published to GitHub.

The following are excluded from version control:

```text
memento.db
data/
.env
```

This helps prevent personal diary content, photos, and private credentials from being accidentally uploaded.

---

## 🗺️ Development Roadmap

### Phase 1 — Core Memory System

- [x] Daily journal structure
- [x] SQLite database
- [x] Text memories
- [x] Photo memories
- [x] Music links
- [x] Video links
- [x] Create memories
- [x] View memories
- [x] Edit memories
- [x] Delete memories
- [x] Local media storage

### Phase 2 — Application Architecture

- [ ] Modularize database layer
- [ ] Separate memory services
- [ ] Separate media services
- [ ] Improve data models
- [ ] Add validation
- [ ] Improve error handling
- [ ] Add automated tests

### Phase 3 — User Interface

- [ ] Web-based interface
- [ ] Daily journal timeline
- [ ] Photo preview
- [ ] Music and video links
- [ ] Journal editing interface
- [ ] Calendar-based navigation

### Phase 4 — AI Journal Generation

- [ ] LLM integration
- [ ] Structured journal generation
- [ ] Automatic summarization
- [ ] Mood detection
- [ ] Theme extraction
- [ ] Personalized writing styles

### Phase 5 — Multimodal Memory Intelligence

- [ ] Image understanding
- [ ] Multimodal context integration
- [ ] Semantic embeddings
- [ ] Similar memory retrieval
- [ ] Cross-day memory connections
- [ ] Long-term personal memory
- [ ] Personalized journal generation

---

## 🎯 Project Goals

Memento AI is both a personal productivity tool and an exploration of how AI can interact with human memories.

The project explores several areas of applied AI and software engineering:

- Large Language Models
- Multimodal AI
- Natural Language Processing
- Information Retrieval
- Semantic Embeddings
- Structured Data Modeling
- Human-AI Interaction
- Personal Knowledge Systems

The ultimate goal is to create a system where users can:

**record first, reflect later.**

Instead of requiring users to immediately write a polished diary entry, Memento AI allows them to collect small fragments throughout the day and lets AI help transform those fragments into a meaningful story.

---

## 📌 Project Status

**Current Version: v0.1 — Core Memory System**

Memento AI is actively under development.

The current version provides the foundational memory storage and management system, including daily journals, editable memories, multimedia memory types, SQLite persistence, and local media storage.

AI-powered journal generation, multimodal understanding, and the web interface are planned for future iterations.

---

## 🌱 Why Memento AI?

Digital journaling usually assumes that users will sit down and write a complete diary entry.

Real life is different.

A person may remember:

```text
08:30
A random thought

12:15
A photo from lunch

17:40
A song that matched the mood

21:30
A short reflection
```

These fragments collectively represent a day.

Memento AI explores whether AI can help transform these fragmented memories into a coherent and personalized representation of that day.

> **Capture the moments. Let AI connect the memories.**