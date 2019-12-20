# InvMan

### Installation
##### Create a virtual environment
`python3 -m venv env`
##### Activate the environment
`. env/bin/activate`
##### Install the project in the virtual environment
`pip install -e .`
##### Run the project
`export FLASK_APP=invman`
###### Initialize the database and run
`flask init-db`
`flask run`

### Usage
##### Step 1: Register a business.
![register](/screens/register.png?raw=true "Register")
##### Step 2: Login
![login](/screens/login.png?raw=true "Login")
##### This is the product page. Here you can add and update products.
![addproducts](/screens/addproducts.png?raw=true)
![addedproducts](/screens/listofproducts.png?raw=true)
##### This is the location page. Here you can add and update locations.
![addlocations](/screens/addlocations.png?raw=true)
![addedlocations](/screens/locationsadded.png?raw=true)
##### This the movement page. Here you can move products to locations.
![movement](/screens/movementpage.png?raw=true)
##### Products at locations with respective quantities.
![productsatlocation](/screens/productsatlocation.png?raw=true)
##### Movement logs.
![movementlogs](/screens/movementlogs.png?raw=true)
