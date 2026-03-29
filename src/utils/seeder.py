import random
from datetime import datetime, timedelta
from model.userdto import UserDto
from model.categorydto import CategoryDto
from model.accountdto import AccountDto
from model.transactiondto import TransactionDto
from model.savingsgoaldto import SavingsGoalDto

def seed_demo_data(srp):
    email = "demo@kashy.com"
    password = "demo"

    # 1. Check if user exists
    existing = UserDto.current_user(srp, email)
    if existing:
        return

    print(f"🌱 Seeding demo data for {email}...")
    user = UserDto(email, password)
    srp.save(user)
    user_id = user.get_id()

    # 2. Accounts
    accounts_data = [
        ("Cuenta Principal", 2500.0),
        ("Ahorros BBVA", 12000.0),
        ("Inversiones", 5400.0),
        ("Efectivo", 150.0)
    ]
    
    accounts = []
    for name, balance in accounts_data:
        acc = AccountDto(name, balance, user_id)
        srp.save(acc)
        accounts.append(acc)

    # 3. Categories
    categories_data = [
        ("Nómina", "ingreso", "#69f0ae", "payments"),
        ("Freelance", "ingreso", "#40c4ff", "trending_up"),
        ("Alimentación", "gasto", "#ff6e40", "restaurant"),
        ("Alquiler", "gasto", "#ff5252", "home"),
        ("Transporte", "gasto", "#448aff", "directions_car"),
        ("Ocio", "gasto", "#b388ff", "sports_esports"),
        ("Suscripciones", "gasto", "#ff4081", "subscriptions"),
        ("Salud", "gasto", "#ff1744", "medication"),
        ("Restaurantes", "gasto", "#ff9100", "lunch_dining"),
        ("Gimnasio", "gasto", "#00e676", "fitness_center")
    ]
    
    cats = []
    for name, ctype, color, icon in categories_data:
        cat = CategoryDto(name, ctype, color, user_id, icon)
        srp.save(cat)
        cats.append(cat)

    # 4. Transactions
    now = datetime.now()
    num_transactions = 60 # Reduced for startup speed
    
    cat_ingresos = [c for c in cats if c.cat_type == 'ingreso']
    cat_gastos = [c for c in cats if c.cat_type == 'gasto']
    
    for i in range(num_transactions):
        days_ago = random.randint(0, 120)
        date = now - timedelta(days=days_ago)
        acc = random.choice(accounts)
        
        if random.random() < 0.15:
            cat = random.choice(cat_ingresos)
            amount = 1800.0 + random.uniform(-50, 50) if cat.name == "Nómina" else 200.0 + random.uniform(0, 300)
            notes = f"Ingreso demo {cat.name}"
        else:
            cat = random.choice(cat_gastos)
            if cat.name == "Alquiler": amount = -850.0
            elif cat.name == "Alimentación": amount = -random.uniform(20, 100)
            else: amount = -random.uniform(5, 60)
            notes = f"Gasto demo {cat.name}"
            
        t = TransactionDto(
            amount=amount,
            notes=notes,
            date_str=date.strftime("%Y-%m-%d"),
            cat_oid=cat.__oid__,
            acc_oid=acc.__oid__,
            user_oid=user_id
        )
        srp.save(t)

    # 5. Goals
    goals_data = [
        ("Coche Nuevo", 15000.0, 4500.0, "directions_car", "#448aff"),
        ("Fondo Emergencia", 10000.0, 8500.0, "security", "#69f0ae"),
        ("MacBook Pro", 2500.0, 1200.0, "laptop_mac", "#ca98ff")
    ]
    
    for name, target, current, icon, color in goals_data:
        goal = SavingsGoalDto(name, target, current, icon, color, user_id)
        srp.save(goal)
    
    print("✅ Demo data seeded successfully.")
