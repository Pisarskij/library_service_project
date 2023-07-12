## Library Service project based on Django Rest Framework API with Telegram Notifications and Stripe Payment Integration

This repository contains a Library Service project based on Django Rest Framework API with integrates Telegram notifications and the Stripe payment system.

### Installation

1. Clone the repository to your local machine:

```bash
git clone https://github.com/Soobig666/library_service_project.git
```

2. Install the dependencies using the package manager `pip`:

```bash
pip install -r requirements.txt
```

3. Create and apply the database migrations:

```bash
python manage.py migrate
```

### Installation Stripe CLI for MacOS (if you use test stipe API)
1. Install Stripe
```bash
brew install stripe/stripe-cli/stripe
```
2. Create webhook-endpoint on [Stripe](https://stripe.com)


### Configuration

1. Create a `.env` file in the root directory of the project:

Explain variables in ".env":
- SECRET_KEY can be generated [here](https://djecrety.ir). SECRET_KEY is need to safety work Django.
- TELEGRAM_BOT_TOKEN & TELEGRAM_CHAT_ID you should take from [BotFather](https://t.me/botfather), after bot created.
- STRIPE_LIVE_SECRET_KEY & STRIPE_TEST_SECRET_KEY you should take from [here](https://dashboard.stripe.com/test/dashboard). But first you need registrate
  (STRIPE_LIVE_SECRET_KEY for testing don`t need, enough only set STRIPE_TEST_SECRET_KEY)
- STRIPE_WEBHOOK_SECRET you should take from terminal after start Stripe CLI (in Usage, paragraph 3) .

2. Replace the placeholder values (
`SECRET_KEY`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`, `STRIPE_LIVE_SECRET_KEY`, `STRIPE_TEST_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`
) with your own values.

### Usage

To start the Django development server, run the following command:
1. Start Django server
```bash
python manage.py runserver
```
You can now access the API at `http://127.0.0.1:8000/`.

2. You need to start Stripe listen to correctly Payment creation (if you have another IP it can be change)
```bash
stripe listen --forward-to 127.0.0.1:8000/webhook
```

3. If you need to start Django-Q (async tasks using Telegram API)
- Create admin user & Create schedule for running sync in DB
- Start Django-Q
```bash
python manage.py qcluster &
```

## Payments

- Stripe have test payments card. You can take it [here](https://stripe.com/docs/testing)


## API Documentation

The following API endpoints are available:

- `/admin/`: Django administration interface. Use this endpoint to access the admin panel and manage your application.

- `/api/schema/`: API schema endpoint. This endpoint provides the schema of your API in a JSON format. You can use it to generate API documentation or for other purposes.

- `/api/doc/swagger/`: Swagger UI documentation endpoint. This endpoint provides interactive API documentation using the Swagger UI interface. It allows you to explore and test your API endpoints.

- `/api/doc/redoc/`: ReDoc documentation endpoint. This endpoint provides another option for interactive API documentation using the ReDoc interface. It offers a clean and modern documentation layout.

- `/api/users/`:  Registration endpoint intended to registrate new users.

- `/api/users/token/`: Authorization endpoint intended to authorize exist users to give new JWT token.

- `/api/users/token/refresh/`: Her you can refresh exist JWT token.

- `/api/users/me/`: This endpoint show to you information about your profile.

- `/api/books/`: This URL is used to retrieve a list of all books.

- `/api/books/<pk>/`: This URL is used to retrieve details of a specific book based on its identifier (pk).

- `/api/borrowing`: This URL is used to retrieve a list of all borrowings.

- `/api/borrowing/?is_active=<true or false>&user_id=<pk>`: In "borrowing-list" can filter by <is_active> and by <user_id>

- `/api/borrowing/<pk>/`: This URL is used to retrieve details of a specific borrowing based on its identifier (pk). 

- `/api/payment/`: This URL is used to retrieve a list of all payments.

- `/api/payment/<pk>/`: This URL is used to retrieve details of a specific payment based on its identifier (pk).

You can access these endpoints by appending them to the base URL of your API. For example, if your API is hosted at `http://127.0.0.1:8000/`, the Swagger UI documentation can be accessed at `http://127.0.0.1:8000/api/doc/swagger/`.


### Additional Resources

- Django Rest Framework documentation: [https://www.django-rest-framework.org/](https://www.django-rest-framework.org/)
- Telegram Bot API documentation: [https://core.telegram.org/bots/api](https://core.telegram.org/bots/api)
- Stripe API documentation: [https://stripe.com/docs/api](https://stripe.com/docs/api)
- Telegram API documentation: [https://core.telegram.org/api](https://core.telegram.org/api)