### **Customer Feedback Management System**

**\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\***



#### **1.Requirements**

**---------------------**

Python 3.10



SQLite (built-in with Python)



Required Python modules:

pip install tabulate



#### **2.Database Schema**

**--------------**

**Tables**

**-----**



**1.Users**

---

id (PK)

username (UNIQUE)

password

role  → admin | customer





**2.Customers**

---

customer\_id (PK)

user\_id (FK → Users.id)

fullname

phone



**3.Category**

---

category\_id (PK)

category\_name (UNIQUE)





**4.Product**

---

product\_id (PK)

product\_name (UNIQUE)

category\_id (FK → Category.category\_id)

price

description





**5.Feedback**

---

feedback\_id (PK)

customer\_id (FK → Customers.customer\_id)

product\_id (FK → Product.product\_id)

rating (1–5)

comment

UNIQUE(customer\_id, product\_id) -> A customer can give only one feedback per product





#### **3.FEATURES**

**-------------------**



**Admin Features**



* Register and login as admin
* Add product categories
* Add products under categories
* View all categories
* View all products
* View all customer feedback
* View feedback by product
* Delete any feedback



**Customer Features**



* Register and login as customer
* View categories
* View products by category
* Add feedback (only once per product)
* View own feedback
* Search own feedback by product
* Update own feedback
* Delete own feedback
* View all customers’ feedback



#### 







