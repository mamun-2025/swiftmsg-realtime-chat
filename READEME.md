
# SwiftMsg - Real-time Chat Backend

SwiftMsg is a high-performance backend for a modern chat application. Built with **Django** and **Docker**, it uses cloud-based solutions like **Neon DB** and **Upstash Redis** to ensure speed and scalability.

## 🚀 Status: Core Infrastructure Ready
The project's foundation is complete and fully containerized:
- **Dockerized Setup:** Seamlessly runs `web`, `worker`, and `redis` services.
- **Cloud Database:** Fully connected to **Neon PostgreSQL** with secure SSL.
- **Cloud Cache & Broker:** Integrated with **Upstash Redis** for fast caching and Celery tasks.
- **Advanced User Model:** Custom `AbstractUser` with support for phone numbers, profile pictures , and online status.
- **Database Design:** Ready-to-use models for `User`, `Conversation`, and `Messages`.

## 📌 Tech Stack
- **Django 5.2.0:** The core web framework
- **PostgreSQL (Neon):** Cloud-native relational database.
- **Redis (Upstash):** Cloud-based message broker and cache.
- **Docker:** For consistent development and deployment.
- **Celery:** To handle background tasks.
- **Pytest 8.1.1:** Core testing framework with `pytest-django`

## ⚙️ How to Run

1. **Setup Environment:**
   Create a `.env` file in the root folder:
   ```env
   SECCRET_KEY=your_secret_key
   DATABASE_URL=postgres://your_neon_db_url
   REDIS_URL=redis://your_upstash_url 

2. Start the Project:
- docker-compose up --build -d

3. Database Migration:
- docker-compose exec web python manage.py migrate

3. How to Run Pytest:
- docker-compose exec web pytest -v --reuse-db

## 🛤 Roadmap (Coming Soon)

- [x] Security: Implementing JWT Authentication.

- [x] API Endpoints: Building DRF Serializers and Views.

- [x] Swagger Documentation: Swagger API documentation using drf-spectacular.

- [x] Real-time: Adding WebSockets with Django Channels.

- [x] Testing: Automated REST API and Async WebSocket testing using Pytest. 

- [ ] Storage: Cloud media storage with AWS S3 or Cloudinary.










