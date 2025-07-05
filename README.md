# Autonomous Task Agent

A Python-based autonomous task management system that generates, prioritizes, and executes tasks toward a specified objective using Mistral for text generation and embeddings, and Supabase with `pgvector` for vector storage.

## Features
- Generates tasks based on an objective (e.g., "Solve world hunger").
- Prioritizes tasks to align with the objective.
- Executes tasks using Mistral's Mixtral-8x7B-Instruct model.
- Stores task results as embeddings in Supabase for context retrieval.
- Containerized with Docker for easy deployment.

## Prerequisites
- Python 3.11+
- Mistral API key (from `api.mixtral.ai`)
- Supabase project with URL and anon key (from `supabase.com`)
- Docker (optional, for containerized deployment)

## Setup

1. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/autonomous-task-agent.git
   cd autonomous-task-agent
