from models import (Base, session,
                    engine, Product)
import csv
import datetime
import time


def menu():
    while True:
        print('''
            \nSTORE INVENTORY
            \rV) View product
            \rA) Add product to database
            \rB) Back up database
            \rE) Exit app
        ''')
        choice = input("What do you want to do? ").lower()
        if choice in ['v', 'a', 'b', 'e']:
            return choice
        else:
            input('''
                \nPlease choose 'V', 'A', 'B' or 'E'
                \rPress enter to continue...  ''')


def clean_date(date_str):
    try:
        date_list = date_str.split('/')
        month = int(date_list[0])
        day = int(date_list[1])
        year = int(date_list[2])
    except ValueError:
        input('''
            \n****** DATE ERROR! ******
            \rPlease enter a valid date not in the future!
            \rUse month/day/year format. Ex: 1/15/2021
            \rPress any key to continue... ''')
        return
    else:
        return datetime.date(year, month, day)


def clean_price(price_str):
    try:
        price_list = price_str.split('$')
        price_float = float(price_list[1])
    except IndexError:
        input('''
            \n****** PRICE ERROR! ******
            \rPlease enter a valid price!
            \rUse $1.99 format. Ex: $4.99
            \rPress any key to continue...  ''')
        return
    else:
        return int(price_float * 100)


def clean_quantity(quantity):
    try:
        quantity = int(quantity)
    except ValueError:
        input('''
            \n****** QUANTITY ERROR! ******
            \rPlease enter an integer (whole number).
            \rEx: 12
            \rPress any key to continue...  ''')
        return
    else:
        return int(quantity)


def clean_id(id_str, id_options):
    try:
        product_id = int(id_str)
    except ValueError:
        input('''
            \n***** ID ERROR *****
            \rInvalid entry please enter an integer (whole number)
            \rPress any key to try again...
            \r*******************''')
        return
    else:
        if product_id in id_options:
            return product_id
        else:
            input(f'''
                \n****** ID ERROR! ******
                \rPlease enter a valid optiion {id_options}.
                \rPress any key to continue...  ''')
            return


def check_product(name_str):
    name_list = []
    products = session.query(Product)
    for product in products:
        name_list.append(product.product_name)
    if name_str in name_list:
        return True
    else:
        return False
    # print(name_list)


def backup_csv():
    header = ['product_name', 'product_price', 'product_quantity', 'date_updated']
    data = session.query(Product.product_name, Product.product_price, Product.product_quantity, Product.date_updated).all()

    with open('store-inventory///backup.csv', 'w', newline="") as csvfile:

        writer = csv.writer(csvfile)
        writer.writerow(header)
        writer.writerows(data)

    print('Database successfully backed up!')
    time.sleep(1.5)


def add_csv():
    with open('store-inventory//inventory.csv') as csvfile:
        data = csv.reader(csvfile)
        next(csvfile)
        for row in data:
            product_in_db = session.query(Product).filter(Product.product_name==row[0]).one_or_none()
            if product_in_db == None:
                product_name = row[0]
                product_price = clean_price(row[1])
                product_quantity = clean_quantity(row[2])
                date_updated = clean_date(row[3])
                new_product = Product(product_name=product_name, product_price=product_price, product_quantity=product_quantity, date_updated=date_updated)
                session.add(new_product)
        session.commit()


def app():
    app_running = True
    while app_running:
        choice = menu()
        if choice == 'v':
            id_list = []
            print('View product by Id')
            id_list = []
            for product in session.query(Product):
                id_list.append(product.product_id)
            id_error = True
            while id_error:
                product_choice = input(f'''
                        \nId Options: {id_list}
                        \rProduct id:  ''')
                product_choice = clean_id(product_choice, id_list)
                if type(product_choice) == int:
                    id_error = False
            product_to_show = session.query(Product).filter(Product.product_id==product_choice).first()
            input(f'''
                \nProduct: {product_to_show.product_name}
                \rPrice: ${product_to_show.product_price / 100}
                \rQuantity: {product_to_show.product_quantity}
                \rLast updated: {product_to_show.date_updated}
                \rPress any key to continue... ''')
        elif choice == 'a':
            name = input('Product name: ')
            price_error = True
            while price_error:
                price = input('Price (ex: $4.99): ')
                price = clean_price(price)
                if type(price) == int:
                    price_error = False
            quantity_error = True
            while quantity_error:
                quantity = input('Quantity: ')
                quantity = clean_quantity(quantity)
                if type(quantity) == int:
                    quantity_error = False
            date_error = True
            while date_error:
                date = input('Date Updated (ex: month/day/year): ')
                date = clean_date(date)
                if type(date) == datetime.date:
                    date_error = False
            if check_product(name):
                product_to_update = session.query(Product.product_name, Product.date_updated).filter(Product.product_name==name).first()
                #print(product_to_update)

                if product_to_update.date_updated <= date:
                    product_to_update.date_updated = date
                    session.commit()
                    backup_csv()
                else:
                    product_to_update.product_price = price
                    product_to_update.product_quantity = quantity
                    session.commit()
                    print('The else clause is running')
                    backup_csv()
            else:
                new_product = Product(product_name=name, product_price=price, product_quantity=quantity, date_updated=date)
                session.add(new_product)
                session.commit()
                print("Product successfully added")
                time.sleep(1.5)

                # find and return the dupicate by name
                # only update the price, quantity, and date
        elif choice == 'b':
            backup_csv()
        else:
            print("Bye bye! Have a good day!")
            app_running = False


if __name__ == "__main__":
    Base.metadata.create_all(engine)
    add_csv()
    app()
