# .ai — Documentation Structure

This folder contains all project documentation organized by category.

## Folder Structure

```
.ai/
├── 01-product/           # Product requirements and planning
│   ├── prd.md            # Product Requirements Document
│   └── tech-stack.md     # Technology stack overview
│
├── 02-architecture/      # Technical architecture
│   ├── ai-implementation.md   # AI/LLM integration specs
│   └── decisions/        # Architecture Decision Records (ADRs)
│       ├── 0001-*.md
│       ├── 0002-*.md
│       └── ...
│
├── 03-governance/        # Process rules and checklists
│   ├── governance.md     # Main governance document (source of truth)
│   ├── after-each-change.md  # CI green checklist
│   └── release.md        # Release process
│
├── 04-testing/           # Test strategies and plans
│   ├── test-strategy.md  # Overall test strategy
│   ├── e2e-tests.md      # E2E testing guide
│   └── test-plan.md      # Detailed test plan
│
├── 05-security/          # Security and CI/CD
│   ├── security-baseline.md  # Security requirements
│   └── cicd-security-plan.md # CI/CD pipeline security
│
├── 06-deployment/        # Deployment and configuration
│   ├── deployment.md     # Fly.io deployment guide
│   ├── env-config.md     # Environment configuration
│   └── dev-commands.md   # Local development commands
│
├── 07-ui/                # UI specifications
│   ├── ui-fixes.md       # UI bug fixes and improvements
│   └── auth-ui-mvp-to-production.md  # Auth UI specs
│
└── diagrams/             # Architecture diagrams
    ├── README.md
    ├── auth.md
    ├── database.md
    ├── ui.md
    └── example.md
```

## Naming Conventions

- **Folders**: Numbered prefixes (`01-`, `02-`, etc.) for logical ordering
- **Files**: Lowercase with hyphens (`kebab-case`)
- **ADRs**: Numbered format (`0001-description.md`)

## Key Documents

| Document | Purpose |
|----------|---------|
| [governance.md](./03-governance/governance.md) | Main contract for all changes |
| [prd.md](./01-product/prd.md) | Product requirements (MVP) |
| [tech-stack.md](./01-product/tech-stack.md) | Technology decisions |
| [after-each-change.md](./03-governance/after-each-change.md) | CI checklist |
