# SurfMarc

SurfMarc is a web application that helps users make informed purchase decisions by providing comprehensive product information, price tracking, and sentiment analysis.

## Features

- **Price Tracking**: Monitor price changes and get notified when prices drop to your desired level.
- **Product Analysis**: Get detailed product information, specifications, and comparisons across different sellers.
- **Sentiment Analysis**: Analyze customer reviews and feedback to understand product sentiment and make data-driven decisions.

## Tech Stack

- **Frontend**: Next.js 14 with TypeScript and Tailwind CSS
- **Backend**: FastAPI with Python 3.11.2
- **Database**: Supabase
- **Authentication**: JWT with FastAPI
- **Containerization**: Docker and Docker Compose (Backend only)

## Project Structure

```
surfmarc/
├── .env                  # Environment variables
├── docker-compose.yml    # Docker Compose configuration
├── server/              # Backend server code
│   ├── Dockerfile
│   ├── .dockerignore
│   ├── requirements.txt
│   └── app/
│       ├── api/
│       ├── core/
│       ├── crud/
│       ├── db/
│       ├── models/
│       └── schemas/
└── app/                 # Frontend code
    ├── components/
    ├── globals.css
    └── page.tsx
```

## Prerequisites

- Node.js 18.x or later
- Python 3.11.2
- Docker and Docker Compose
- Supabase account and credentials

## Environment Variables

Create a `.env` file in the root directory with the following variables:

```env
# Supabase Configuration
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key

# JWT Configuration
SECRET_KEY=your_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=43200

# URLS
SERVER_URL=http://localhost:8000
CLIENT_URL=http://localhost:3000
```

## Getting Started

### Backend Setup

#### Using Docker (Recommended)

1. Make sure Docker Desktop is running
2. Build and start the container:
   ```bash
   docker-compose up --build
   ```
3. Access the API at http://localhost:8000
4. View API documentation at http://localhost:8000/docs

The container is configured with hot-reload enabled, so any changes you make to the server code will automatically restart the application.

#### Manual Setup

1. Create and activate a virtual environment:

   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # Unix/MacOS
   python3 -m venv venv
   source venv/bin/activate
   ```

2. Install dependencies:

   ```bash
   cd server
   pip install -r requirements.txt
   ```

3. Start the FastAPI server:
   ```bash
   uvicorn main:app --reload
   ```

### Frontend Setup

1. Install dependencies:

   ```bash
   cd app
   npm install
   ```

2. Start the development server:

   ```bash
   npm run dev
   ```

3. Access the application at http://localhost:3000

## API Endpoints

- `POST /api/v1/auth/register`: Register a new user
- `POST /api/v1/auth/login`: Login and get access token
- `GET /api/v1/users/me`: Get current user information

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
