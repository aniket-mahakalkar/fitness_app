from models.models import Customer
from db import db

def create_customer(name, email):
    customer = Customer.query.filter_by(email=email).first()
    if not customer:
        customer = Customer(name=name, email=email)
        db.session.add(customer)
        db.session.commit()
    return customer

def get_all_customers():
    try:

        customers = Customer.query.all()
        if not customers:
            return []

        all_customers = []
        for c in customers:
            all_customers.append({
                "id": c.id,
                "name": c.name,
                'email': c.email,
                'created_at': c.created_at.strftime('%Y-%m-%d %H:%M')
            })
        return all_customers

    except Exception as e:
        print(f'Error: {e}')
        return None

def get_customer_by_email(email):
    return Customer.query.filter_by(email=email).first()
