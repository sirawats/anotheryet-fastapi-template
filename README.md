# yet-another-fastapi-template

**yet-another-fastapi-template** is a highly opinionated, modern FastAPI template designed to kickstart your next Python web application with best practices and a well-structured codebase. This template is built with a carefully selected stack of cutting-edge tools and libraries, aiming to provide an optimal balance of performance, maintainability, and developer productivity.

## Features

🐍 **Python 3.12**: Leverage the latest features and improvements in Python for enhanced performance and productivity.

#### Package Management
- ⚡ **UV**: Lightning-fast Python package installer and resolver written in Rust

#### Backend Framework
- 🚀 **FastAPI**: High-performance web framework for building APIs
- 🗃️ **SQLAlchemy**: Powerful ORM for efficient database interactions
- 🐘 **Asyncpg**: High-performance PostgreSQL driver with async/await support
- 🔄 **Alembic**: Lightweight database migration tool for smooth schema changes

#### Code Quality
- 🦀 **Ruff**: Fast Python linter written in Rust for code quality

#### Testing and Development Tools
- 🧪 **Pytest**: Robust testing framework with async support and coverage reports
- 🐳 **Docker**: Containerization for consistent environments across development and production

## Why Choose yet-another-fastapi-template?

This template is perfect for developers who want to start a new FastAPI project with a solid foundation, adhering to modern best practices. It abstracts the boilerplate setup and configuration, allowing you to focus on building features and writing clean, maintainable code. With this template, you'll have:

- A pre-configured development environment with Docker for easy setup.
- A robust and scalable architecture that follows best practices.
- Tools and configurations that enforce code quality and consistency.
- A seamless workflow for testing and deployment.

## Getting Started

Clone the repository and follow the setup instructions to get your project up and running in minutes. Whether you're building a small API service or a complex, scalable application, **yet-another-fastapi-template** is the perfect starting point for your next project.

## Development

### Setup

```bash
cp .env.example .env
```

### Create Alembic Migration

```bash
uv run -- alembic revision --autogenerate -m "Your migration message"
```

### Apply Alembic Migration

```bash
uv run -- alembic upgrade head
```