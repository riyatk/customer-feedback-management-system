import sqlite3
from tabulate import tabulate


def safe_int_input(msg):
    try:
        return int(input(msg))
    except ValueError:
        print("Enter numbers only")
        return None

conn = sqlite3.connect("feedback.db")
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS Users(
               id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
               username VARCHAR(20) NOT NULL UNIQUE,
               password TEXT NOT NULL,
               role VARCHAR(20) CHECK (role IN ('admin','customer'))
               )
               ''')
cursor.execute('''
CREATE TABLE IF NOT EXISTS Customers(
               customer_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
               user_id INTEGER NOT NULL,
               fullname VARCHAR(20) NOT NULL,
               phone VARCHAR(20),
               FOREIGN KEY(user_id) REFERENCES Users(id)
               )
               ''')
cursor.execute('''
CREATE TABLE IF NOT EXISTS Category(
               category_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
               category_name TEXT UNIQUE NOT NULL
               )
               ''')
cursor.execute('''
CREATE TABLE IF NOT EXISTS Product(
               product_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
               product_name TEXT UNIQUE NOT NULL,
               category_id INTEGER,
               price INTEGER NOT NULL,
               description TEXT NOT NULL,
               FOREIGN KEY(category_id) REFERENCES Category(category_id)
               )
               ''')
cursor.execute('''
CREATE TABLE IF NOT EXISTS Feedback(
               feedback_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
               customer_id INTEGER NOT NULL,
               product_id INTEGER NOT NULL,
               rating CHECK (rating BETWEEN 1 AND 5),
               comment TEXT,
               FOREIGN KEY(customer_id) REFERENCES Customers(customer_id),
               FOREIGN KEY(product_id) REFERENCES Product(product_id),
               UNIQUE(customer_id, product_id)
               )
               ''')

#REGISTER
def register():
    print("****REGISTER****")
    username = input("Enter username: ")
    password = input("Enter password: ")
    role = input("Enter your role(admin/customer): ")

    if role not in ("admin", "customer"):
        print("Invalid role")
        return

    try:
        conn = sqlite3.connect("feedback.db")
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO Users(username, password, role)
            VALUES (?, ?, ?)
        """, (username, password, role))

        user_id = cursor.lastrowid  

        # Insert into Customers ONLY if role is customer
        if role == "customer":
            fullname = input("Enter full name: ")
            phone = input("Enter phone number: ")

            cursor.execute("""
                INSERT INTO Customers(user_id, fullname, phone)
                VALUES (?, ?, ?)
            """, (user_id, fullname, phone))

        conn.commit()
        print("User registered successfully")

    except sqlite3.IntegrityError:
        print("Username already exists")

    except sqlite3.Error as e:
        print(" Database error:", e)

    finally:
        conn.close()



#LOGIN
def login():
    try:
        conn = sqlite3.connect("feedback.db")
        cursor = conn.cursor()

        username = input("Enter username: ")
        password = input("Enter password: ")
        role = input("Role(admin/customer): ")


        cursor.execute("""
            SELECT id, role
            FROM Users
            WHERE username = ? AND password = ? AND role = ?
        """, (username, password, role))

        user = cursor.fetchone()

        if not user:
            print("Invalid login credentials")
            return None

        return user[0]

    except sqlite3.Error as e:
        print("Login error:", e)
        return None

    finally:
        conn.close()


################################################ ADMIN #####################################################

#ADD CATEGORY(ADMIN)
def addCategory():
    name = input("Enter category name: ")

    try:
        conn = sqlite3.connect("feedback.db")
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO Category(category_name) VALUES (?)", (name,)
        )
        conn.commit()
        print("Category added")
        cursor.execute('''
                        SELECT * FROM Category
                       ''')
        rows = cursor.fetchall()
        headers = ["ID","Category Name"]
        print(tabulate(rows, headers=headers, tablefmt="grid"))

    except sqlite3.IntegrityError:
        print("Category already exists")

    finally:
        conn.close()


#ADD PRODUCT(ADMIN)
def addProduct():
    try:
        name = input("Enter product name: ")
        category_id = int(input("Enter category id: "))
        price = int(input("Enter price: "))
        desc = input("Enter description: ")

        conn = sqlite3.connect("feedback.db")
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO Product(product_name, category_id, price, description)
            VALUES (?, ?, ?, ?)
        """, (name, category_id, price, desc))

        conn.commit()
        print("Product added")
    except ValueError:
        print("Category ID & price must be numbers")

    except sqlite3.IntegrityError:
        print("Product already exists OR invalid category ID")

    finally:
        conn.close()

#VIEW ALL CATEGORY(ADMIN)
def viewCategory():

    conn = sqlite3.connect("feedback.db")
    cursor = conn.cursor()
    cursor.execute('''
                    SELECT * FROM Category 
                   ''')
    rows = cursor.fetchall()
    if not rows:
        print("No Category found")
    else:
        print("\n--- ALL CATEGORY ---")
        headers = ["Category ID","Category Name"]
        print(tabulate(rows,headers=headers,tablefmt="grid"))

    conn.close()

#VIEW ALL PRODUCTS(ADMIN)
def viewProducts():

    conn = sqlite3.connect("feedback.db")
    cursor = conn.cursor()
    cursor.execute('''
                    SELECT * FROM Product 
                   ''')
    rows = cursor.fetchall()
    if not rows:
        print("No Category found")
    else:
        print("\n--- ALL PRODUCTS ---")
        headers = ["ProductID","Product Name","CategoryID","Price","Description"]
        print(tabulate(rows, headers=headers, tablefmt="grid"))

    conn.close()

#VIEW ALL FEEDBACK(ADMIN)
def adminViewFeedback():
    conn = sqlite3.connect("feedback.db")

    cursor = conn.cursor()

    cursor.execute("""
    SELECT F.feedback_id, P.product_name, C.fullname, F.rating, F.comment
    FROM Feedback F
    JOIN Product P ON F.product_id = P.product_id
    JOIN Customers C ON F.customer_id = C.customer_id
    """)

    rows = cursor.fetchall()

    if not rows:
        print("No feedback found")
    else:
        print("\n--- ALL FEEDBACK ---")        
        headers = ["ID","Product","Customer","Rating","Comment"]
        print(tabulate(rows, headers=headers, tablefmt="grid"))


    conn.close()

#VIEW ALL FEEDBACK BY PRODUCT(ADMIN)
def adminViewFeedbackByProduct():
    pname = input("Enter product name: ")

    conn = sqlite3.connect("feedback.db")

    cursor = conn.cursor()


    cursor.execute(
        "SELECT product_id FROM Product WHERE product_name LIKE ?",
        (f"%{pname}%",)
    )
    product = cursor.fetchone()

    if not product:
        print("Product not found")
        conn.close()
        return

    product_id = product[0]

    cursor.execute("""
    SELECT C.fullname, F.rating, F.comment
    FROM Feedback F
    JOIN Customers C ON F.customer_id = C.customer_id
    WHERE F.product_id = ?
    """, (product_id,))

    rows = cursor.fetchall()

    if not rows:
        print("No feedback for this product")
    else:
        print("\n--- FEEDBACK FOR PRODUCT ---")
        headers = ["Customer","Rating","Comment"]
        print(tabulate(rows, headers=headers, tablefmt="grid"))
    conn.close()


#DELETE FEEDBACK(ADMIN)
def adminDeleteFeedback():
    
    fid = safe_int_input("Enter feedback ID to delete: ")
    if fid is None:
        return

    conn = sqlite3.connect("feedback.db")

    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM Feedback WHERE feedback_id = ?",
        (fid,)
    )

    if cursor.rowcount == 0:
        print("Feedback ID not found")
    else:
        conn.commit()
        print("Feedback deleted successfully")

    conn.close()


########################################## END ADMIN ###########################################

#ADD FEEDBACK(CUSTOMER)
def addFeedback(user_id):
    conn = sqlite3.connect("feedback.db")

    cursor = conn.cursor()

    cursor.execute(
        "SELECT customer_id FROM Customers WHERE user_id = ?",
        (user_id,)
    )
    if not cursor.fetchone():
        print("Customer profile not found")
        conn.close()
        return

    product_id = safe_int_input("Enter product id: ")
    if product_id is None:
        return


    while True:
        try:
            rating = int(input("Rating (1-5): "))
            if 1 <= rating <= 5:
                break
            else:
                print("Rating must be between 1 and 5")
        except ValueError:
            print("Enter numbers only")

    comment = input("Comment: ")

    cursor.execute("""
        SELECT feedback_id
        FROM Feedback
        WHERE customer_id = (
            SELECT customer_id FROM Customers WHERE user_id = ?
        )
        AND product_id = ?
    """, (user_id, product_id))

    if cursor.fetchone():
        print("You have already given feedback for this product")
        conn.close()
        return

    cursor.execute("""
        INSERT INTO Feedback(customer_id, product_id, rating, comment)
        VALUES (
            (SELECT customer_id FROM Customers WHERE user_id=?),
            ?, ?, ?
        )
    """, (user_id, product_id, rating, comment))

    conn.commit()
    print("Feedback added successfully")


#VIEW OWN FEEDBACK(CUSTOMER)
def viewFeedback(user_id):
    conn = sqlite3.connect("feedback.db")

    cursor = conn.cursor()

    cursor.execute(
        "SELECT customer_id FROM Customers WHERE user_id = ?",
        (user_id,)
    )
    if not cursor.fetchone():
        print("Customer profile not found")
        conn.close()
        return

    cursor.execute("""
        SELECT feedback_id, product_id, rating, comment
        FROM Feedback
        WHERE customer_id = (
            SELECT customer_id FROM Customers WHERE user_id = ?
        )
    """, (user_id,))

    rows = cursor.fetchall()

    if not rows:
        print("No feedback yet")
    else:
        headers = ["FeedbackID","ProductID","Rating","Comment"]
        print(tabulate(rows, headers=headers, tablefmt="grid"))
            
    conn.close()
    


#SEARCH FEEDBACK(BY PRODUCT ID)
def searchFeedback(user_id):
    conn = sqlite3.connect("feedback.db")

    cursor = conn.cursor()

    cursor.execute(
        "SELECT customer_id FROM Customers WHERE user_id = ?",
        (user_id,)
    )
    if not cursor.fetchone():
        print("Customer profile not found")
        conn.close()
        return

    product_id = safe_int_input("Enter product id to search: ")
    if product_id is None:
        return


    cursor.execute("""
        SELECT feedback_id, rating, comment
        FROM Feedback
        WHERE product_id = ?
        AND customer_id = (
            SELECT customer_id FROM Customers WHERE user_id = ?
        )
    """, (product_id, user_id))

    rows = cursor.fetchall()

    if not rows:
        print("No feedback found for this product")
    else:
        headers = ["FeedbackID","Rating","Comment"]
        print(tabulate(rows, headers=headers, tablefmt="grid"))

    



#UPDATE FEEDBACK(ONLY OWN)
def updateFeedback(user_id):
    conn = sqlite3.connect("feedback.db")

    cursor = conn.cursor()


    cursor.execute(
        "SELECT customer_id FROM Customers WHERE user_id = ?",
        (user_id,)
    )
    if not cursor.fetchone():
        print("Customer profile not found")
        conn.close()
        return


    fid = safe_int_input("Enter feedback id: ")
    if fid is None:
        return

    while True:
        try:
            rating = int(input("New rating (1-5): "))
            if 1 <= rating <= 5:
                break
            else:
                print("Rating must be between 1 and 5")
        except ValueError:
            print("Enter numbers only")

    comment = input("New comment: ")

    cursor.execute("""
        UPDATE Feedback
        SET rating = ?, comment = ?
        WHERE feedback_id = ?
        AND customer_id = (
            SELECT customer_id FROM Customers WHERE user_id = ?
        )
    """, (rating, comment, fid, user_id))

    if cursor.rowcount == 0:
        print("Feedback not found or not yours")
    else:
        conn.commit()
        print("Feedback updated successfully")

    





#DELETE FEEDBACK(LOGGED IN CUSTOMER ONLY)
def deleteFeedback(user_id):
    conn = sqlite3.connect("feedback.db")

    cursor = conn.cursor()


    cursor.execute(
        "SELECT customer_id FROM Customers WHERE user_id = ?",
        (user_id,)
    )
    if not cursor.fetchone():
        print("Customer profile not found")
        conn.close()
        return

  
    fid = safe_int_input("Feedback ID: ")
    if fid is None:
        return


    cursor.execute("""
        DELETE FROM Feedback
        WHERE feedback_id = ?
        AND customer_id = (
            SELECT customer_id FROM Customers WHERE user_id = ?
        )
    """, (fid, user_id))

    if cursor.rowcount == 0:
        print("Feedback not found or not yours")
    else:
        conn.commit()
        print("Feedback deleted")

    


#VIEW ALL FEEDBACK
def viewAllFeedback():
    conn = sqlite3.connect("feedback.db")

    cursor = conn.cursor()

    cursor.execute("""
        SELECT P.product_name, F.rating, F.comment
        FROM Feedback F
        JOIN Product P ON F.product_id = P.product_id
        """)

    rows = cursor.fetchall()

    if not rows:
        print("No feedback available")
    else:
        print("\n--- ALL CUSTOMER FEEDBACK ---")
        headers = ["Product","Rating","Comment"]
        print(tabulate(rows, headers=headers, tablefmt="grid"))

    conn.close()

#VIEW FEEDBACK BY PRODUCT(ALL CUSTOMERS)
def viewFeedbackByProduct():
    pname = input("Enter product name: ")

    conn = sqlite3.connect("feedback.db")

    cursor = conn.cursor()

    cursor.execute(
        "SELECT product_id FROM Product WHERE product_name LIKE ?",
        (f"%{pname}%",)
    )
    product = cursor.fetchone()

    if not product:
        print("Product not found")
        conn.close()
        return

    product_id = product[0]

    cursor.execute("""
    SELECT rating, comment
    FROM Feedback
    WHERE product_id = ?
    """, (product_id,))

    rows = cursor.fetchall()

    if not rows:
        print("No feedback for this product")
    else:
        print("\n--- FEEDBACK FOR PRODUCT ---")
        headers = ["Rating","Comment"]
        print(tabulate(rows, headers=headers, tablefmt="grid"))

#VIEW ALL CATEGORY(CUSTOMER)
def viewAllCategory():

    conn = sqlite3.connect("feedback.db")
    cursor = conn.cursor()
    cursor.execute('''
                    SELECT category_name FROM Category 
                   ''')
    rows = cursor.fetchall()
    if not rows:
        print("No Category found")
    else:
        print("\n--- ALL CATEGORY ---")
        headers = ["Category Name"]
        print(tabulate(rows,headers=headers,tablefmt="grid"))

    conn.close()

#VIEW ALL PRODUCTS BY CATEGORY(CUSTOMER)
def viewAllProducts():
    cname = input("Enter the category name:")
    conn = sqlite3.connect("feedback.db")
    cursor = conn.cursor()
    cursor.execute('''
                    SELECT category_id FROM Category WHERE category_name = ? 
                   ''',(cname,))
    if not cursor.fetchone():
        print("Category not found")
        conn.close()
        return

    cursor.execute("""
        SELECT product_id, product_name, price,description
        FROM Product
        WHERE category_id = (
            SELECT category_id FROM Category WHERE category_name = ? 
        )
    """, (cname,))

    rows = cursor.fetchall()

    if not rows:
        print("No product found for this category")
    else:
        headers = ["ProductID","RaProduct Name","Price","Description"]
        print(tabulate(rows, headers=headers, tablefmt="grid"))

    conn.close()   







def welcome():
    print("*****WELCOME TO CUSTOMER FEEDBACK MANAGEMENT SYSTEM*****")
    print('''
          1.Register
          2.Login
          3.Exit
          ''')
    ch = safe_int_input("Enter your choice:")
    if ch is None:
        return

    if ch == 1:
        register()
    elif ch == 2:
        user_id = login()
        if user_id:
            conn = sqlite3.connect("feedback.db")

            cursor = conn.cursor()
            cursor.execute("SELECT role FROM Users WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            if not row:
                print("User not found")
                conn.close()
                return
            role = row[0]


            if role == "admin":
                admin_menu()
            else:
                main(user_id)
    elif ch == 3:
        exit()
    else:
        print("Invalid choice")

def main(user_id):
    print("***CUSTOMER FEEDBACK MANAGEMENT SYSTEM***")
    while True:
        print("Choose any:")
        print("""
            1.Add Feedback
            2.View My Feedback
            3.Search My Feedback
            4.Update My Feedback
            5.Delete My Feedback
            6.View All Customers Feedback
            7.View Feedback by Product
            8.View All Category
            9.View All Products by Category
            10.Exit
            """)

        ch = safe_int_input("Enter your choice:-")
        if ch is None:
            continue

        if ch == 1:
            addFeedback(user_id)
        elif ch == 2:
            viewFeedback(user_id)
        elif ch == 3:
            searchFeedback(user_id)
        elif ch == 4:
            updateFeedback(user_id)
        elif ch == 5:
            deleteFeedback(user_id)
        elif ch == 6:
            viewAllFeedback()
        elif ch == 7:
            viewFeedbackByProduct()
        elif ch == 8:
            viewAllCategory()
        elif ch == 9:
            viewAllProducts()
        elif ch == 10:
            break
        else:
            print("Invalid option")



#ADMIN MAIN MENU
def admin_menu():
    while True:
        print("\n*** ADMIN MENU ***")
        print("1.Add Category")
        print("2.Add Product")
        print("3.View Category")
        print("4.view Products")
        print("5.View Feedback")
        print("6.View Feedback By Product")
        print("7.Delete Feedback")
        print("8.Logout")

        ch = safe_int_input("Enter your choice:-")
        if ch is None:
            continue


        if ch == 1:
            addCategory()
        elif ch == 2:
            addProduct()
        elif ch == 3:
            viewCategory()
        elif ch == 4:
            viewProducts()
        elif ch == 5:
            adminViewFeedback()
        elif ch == 6:
            adminViewFeedbackByProduct()
        elif ch == 7:
            adminDeleteFeedback()
        elif ch == 8:
            break
        else:
            print("Invalid choice")
welcome()