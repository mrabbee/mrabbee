import sqlite3
import csv

# Database connection
class DataBaseConnection:
    def _init_(self, db_name):
        try:
            self.connection = sqlite3.connect(db_name)
            self.cursor = self.connection.cursor()
        except sqlite3.Error as e:
            print(f"Error connecting to database: {e}")
            self.connection = None
    
    def close(self):
        if self.connection:
            self.connection.close()

# Table manager class and SQL queries
class TableManager:
    def _init_(self, db_connection):
        self.db_connection = db_connection

    def create_table(self):
        create_customers_table = '''
        CREATE TABLE IF NOT EXISTS customers
        (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE
        );
        '''

        create_products_table = '''
        CREATE TABLE IF NOT EXISTS products
        (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            quantity INTEGER NOT NULL
        );
        '''

        create_orders_table = '''
        CREATE TABLE IF NOT EXISTS orders
        (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL,
            order_date TEXT NOT NULL,
            FOREIGN KEY (customer_id) REFERENCES customers(id)
        );
        '''

        create_order_details_table = '''
        CREATE TABLE IF NOT EXISTS order_details
        (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders(id),
            FOREIGN KEY (product_id) REFERENCES products(id)
        );
        '''

        self.db_connection.cursor.execute(create_customers_table)
        self.db_connection.cursor.execute(create_products_table)
        self.db_connection.cursor.execute(create_orders_table)
        self.db_connection.cursor.execute(create_order_details_table)
        self.db_connection.connection.commit()

# CRUD operations
# Add new customer
class CustomerManager:
    def _init_(self, db_connection):
        self.db_connection = db_connection

    def add_customer(self, name, email):
        query = "INSERT INTO customers (name, email) VALUES (?, ?)"
        self.db_connection.cursor.execute(query, (name, email))
        self.db_connection.connection.commit()

    def update_customer(self, customer_id, name, email):
        query = "UPDATE customers SET name = ?, email = ? WHERE id = ?"
        self.db_connection.cursor.execute(query, (name, email, customer_id))
        self.db_connection.connection.commit()

    def delete_customer(self, customer_id):
        query = "DELETE FROM customers WHERE id = ?"
        self.db_connection.cursor.execute(query, (customer_id,))
        self.db_connection.connection.commit()

# Add a new product
class ProductManager:
    def _init_(self, db_connection):
        self.db_connection = db_connection

    def add_product(self, name, price, quantity):
        query = "INSERT INTO products (name, price, quantity) VALUES (?, ?, ?)"
        self.db_connection.cursor.execute(query, (name, price, quantity))
        self.db_connection.connection.commit()

    def update_product(self, product_id, price, quantity):
        query = "UPDATE products SET price = ?, quantity = ? WHERE id = ?"
        self.db_connection.cursor.execute(query, (price, quantity, product_id))
        self.db_connection.connection.commit()

    def delete_product(self, product_id):
        query = "DELETE FROM products WHERE id = ?"
        self.db_connection.cursor.execute(query, (product_id,))
        self.db_connection.connection.commit()

# Order management
class OrderManager:
    def _init_(self, db_connection):
        self.db_connection = db_connection

    def create_order(self, customer_id, order_date, order_details):
        query = "INSERT INTO orders (customer_id, order_date) VALUES (?, ?)"
        self.db_connection.cursor.execute(query, (customer_id, order_date))
        order_id = self.db_connection.cursor.lastrowid
        for detail in order_details:
            product_id, quantity = detail
            query = "INSERT INTO order_details (order_id, product_id, quantity) VALUES (?, ?, ?)"
            self.db_connection.cursor.execute(query, (order_id, product_id, quantity))
        self.db_connection.connection.commit()

    def update_order(self, order_id, order_details):
        query = "DELETE FROM order_details WHERE order_id = ?"
        self.db_connection.cursor.execute(query, (order_id,))
        for detail in order_details:
            product_id, quantity = detail
            query = "INSERT INTO order_details (order_id, product_id, quantity) VALUES (?, ?, ?)"
            self.db_connection.cursor.execute(query, (order_id, product_id, quantity))
        self.db_connection.connection.commit()

    def delete_order(self, order_id):
        query = "DELETE FROM order_details WHERE order_id = ?"
        self.db_connection.cursor.execute(query, (order_id,))
        query = "DELETE FROM orders WHERE id = ?"
        self.db_connection.cursor.execute(query, (order_id,))
        self.db_connection.connection.commit()

    def fetch_all_orders(self):
        query = """
        SELECT orders.id, customers.name, orders.order_date, products.name, order_details.quantity
        FROM orders
        JOIN customers ON orders.customer_id = customers.id
        JOIN order_details ON orders.id = order_details.order_id
        JOIN products ON order_details.product_id = products.id
        """
        self.db_connection.cursor.execute(query)
        return self.db_connection.cursor.fetchall()

    def generate_report(self):
        orders = self.fetch_all_orders()
        for order in orders:
            print(order)

    def generate_csv_report(self, file_name):
        orders = self.fetch_all_orders()
        with open(file_name, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Order ID", "Customer Name", "Order Date", "Product Name", "Quantity"])
            for order in orders:
                writer.writerow(order)

    def search_orders_by_customer_name(self, customer_name):
        query = """
        SELECT orders.id, customers.name, orders.order_date, products.name, order_details.quantity
        FROM orders
        JOIN customers ON orders.customer_id = customers.id
        JOIN order_details ON orders.id = order_details.order_id
        JOIN products ON order_details.product_id = products.id
        WHERE customers.name LIKE ?
        """
        self.db_connection.cursor.execute(query, (f'%{customer_name}%',))
        return self.db_connection.cursor.fetchall()

# User interface
def main():
    db_connection = DataBaseConnection('order_management.db')
    table_manager = TableManager(db_connection)
    table_manager.create_table()
    
    customer_manager = CustomerManager(db_connection)
    product_manager = ProductManager(db_connection)
    order_manager = OrderManager(db_connection)
    
    while True:
        print("\n1. Add Customer")
        print("2. Update Customer")
        print("3. Delete Customer")
        print("4. Add Product")
        print("5. Update Product")
        print("6. Delete Product")
        print("7. Create Order")
        print("8. Update Order")
        print("9. Delete Order")
        print("10. Display All Orders")
        print("11. Generate CSV Report")
        print("12. Search Order By Customer Name")
        print("13. Exit")
        
        choice = input("Enter your choice: ")
        
        if choice == '1':
            name = input("Enter customer name: ")
            email = input("Enter customer email: ")
            customer_manager.add_customer(name, email)
        
        elif choice == '2':
            customer_id = input("Enter customer ID: ")
            name = input("Enter new customer name: ")
            email = input("Enter new customer email: ")
            customer_manager.update_customer(customer_id, name, email)
        
        elif choice == '3':
            customer_id = input("Enter customer ID: ")
            customer_manager.delete_customer(customer_id)
        
        elif choice == '4':
            name = input("Enter product name: ")
            price = float(input("Enter product price: "))
            quantity = int(input("Enter product quantity: "))
            product_manager.add_product(name, price, quantity)
        
        elif choice == '5':
            product_id = input("Enter product ID: ")
            price = float(input("Enter new product price: "))
            quantity = int(input("Enter new product quantity: "))
            product_manager.update_product(product_id, price, quantity)
        
        elif choice == '6':
            product_id = input("Enter product ID: ")
            product_manager.delete_product(product_id)
        
        elif choice == '7':
            customer_id = input("Enter customer ID: ")
            order_date = input("Enter order date (YYYY-MM-DD): ")
            order_details = []
            while True:
                product_id = input("Enter product ID (or 'done' to finish): ")
                if product_id == 'done':
                    break
                quantity = int(input("Enter quantity: "))
                order_details.append((product_id, quantity))
            order_manager.create_order(customer_id, order_date, order_details)
        
        elif choice == '8':
            order_id = input("Enter order ID: ")
            order_details = []
            while True:
                product_id = input("Enter product ID (or 'done' to finish): ")
                if product_id == 'done':
                    break
                quantity = int(input("Enter quantity: "))
                order_details.append((product_id, quantity))
            order_manager.update_order(order_id, order_details)
        
        elif choice == '9':
            order_id = input("Enter order ID: ")
            order_manager.delete_order(order_id)
            
        elif choice == '10':
         order_manager.generate_report()
    
        elif choice == '11':
         file_name = input("Enter CSV file name: ")
         order_manager.generate_csv_report(file_name)
    
        elif choice == '12':
         customer_name = input("Enter customer name to search: ")
         orders = order_manager.search_orders_by_customer_name(customer_name)
         for order in orders:
            print(order)
    
        elif choice == '13':
         db_connection.close()
        break
    
    else:
        print("Invalid choice. Please try again.")
        if name == "main":
            main()
