# SurfMarc

SurfMarc is a web application that helps users find and compare surfboard information. The project consists of a Next.js frontend and a FastAPI backend.

## Project Structure

```
surfmarc/
├── app/                 # Next.js frontend application
│   ├── components/     # React components
│   ├── globals.css     # Global styles
│   └── page.tsx        # Home page
├── backend/            # FastAPI backend application
│   ├── app/           # Application package
│   │   ├── api/       # API endpoints
│   │   ├── core/      # Core functionality
│   │   ├── crud/      # Database operations
│   │   ├── db/        # Database configuration
│   │   ├── models/    # Pydantic models
│   │   └── schemas/   # Data schemas
│   ├── requirements.txt # Python dependencies
│   └── main.py        # Application entry point
└── README.md          # This file
```

## Frontend (Next.js)

### Prerequisites
- Node.js 18.x or later
- npm or yarn

### Getting Started

1. Install dependencies:
```bash
npm install
# or
yarn install
```

2. Run the development server:
```bash
npm run dev
# or
yarn dev
```

3. Open [http://localhost:3000](http://localhost:3000) in your browser.

## Backend (FastAPI)

### Prerequisites
- Python 3.12.3
- pip

### Getting Started

1. Create and activate a virtual environment:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
Create a `.env` file in the backend directory with:
```
PROJECT_NAME=SurfMarc
VERSION=1.0.0
DESCRIPTION=SurfMarc API for product information retrieval
API_V1_STR=/api/v1

# CORS Configuration
CORS_ORIGINS=["http://localhost:3000"]

# JWT Configuration
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Supabase Configuration
SUPABASE_URL=your-supabase-url
SUPABASE_KEY=your-supabase-key
```

4. Run the development server:
```bash
uvicorn main:app --reload
```

5. Open [http://localhost:8000/docs](http://localhost:8000/docs) for the API documentation.

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register a new user
- `POST /api/v1/auth/login` - Login and get access token

### Users
- `GET /api/v1/users/me` - Get current user information

## Development

### Frontend
- Uses Next.js 14 with App Router
- Styled with Tailwind CSS
- TypeScript for type safety

### Backend
- FastAPI for high-performance API
- Pydantic for data validation
- Supabase for database
- JWT for authentication

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
