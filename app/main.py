from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import sqlite3

"""Database SQLite3"""

def get_connection():
    connection = sqlite3.connect("inventory.db")
    return connection


def manage_database():
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS items (id INTEGER PRIMARY KEY, name TEXT NOT NULL, quantity INTEGER NOT NULL CHECK (quantity >= 0))")
    connection.close()


manage_database()
    


"""Classes"""

class Item(BaseModel):

    name: str 
    quantity: int = Field(ge=0)



class ItemUpdate(BaseModel):

    quantity_update: int = Field(ge=0)




"""APP"""

app = FastAPI(title="RPG Inventory API")



''' GET'''

@app.get("/")
def home():
    return {"message": "RPG Inventory API funcionando!"} 



@app.get("/inventory")
def list_inventory():
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM items")
    data_items = cursor.fetchall()
    items_dict = []
    for item_id, item_name, item_quantity in data_items:
        items_dict.append({"id": item_id, "name": item_name, "quantity": item_quantity})
    connection.close()
    return items_dict




@app.get("/items/{item_name}")
def search_item(item_name):
    item_name = item_name.lower()  
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM items WHERE name = ?", (item_name,))
    founded_item = cursor.fetchone()
    if not founded_item:
        connection.close()
        raise HTTPException(status_code=404, detail="Item not found")    
    connection.close()
    return founded_item


 
''' POST'''


@app.post("/item")
async def create_item(item:Item):
    item.name = item.name.lower()
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT id FROM items WHERE name = ?", (item.name,))
    existing_item = cursor.fetchone()
    if existing_item:
        connection.close()
        raise HTTPException(status_code=409, detail="Item já existe")
    cursor.execute("INSERT INTO items (name, quantity) VALUES (?, ?)", (item.name, item.quantity,))
    connection.commit()
    connection.close()
    return item



"""PATCH"""
@app.patch("/item/{item_name}")
async def edit_item(item_name: str, item_update: ItemUpdate):
    item_name = item_name.lower()
    connection = get_connection()
    cursor = connection.cursor()    
    cursor.execute("SELECT * FROM items WHERE name = ?", (item_name,))
    founded_item = cursor.fetchone()    
    if not founded_item:
        connection.close()
        raise HTTPException(status_code=404, detail="Item não encontrado")
    cursor.execute("UPDATE items SET quantity = ? WHERE name = ?",(item_update.quantity_update,item_name,))
    connection.commit()
    connection.close()
    return {"message": "Item atualizado no inventario"}



"""DELETE"""

@app.delete("/item/{item_name}")
def delete_item(item_name: str):
    item_name = item_name.lower()
    connection = get_connection()
    cursor = connection.cursor()    
    cursor.execute("SELECT * FROM items WHERE name = ?", (item_name,))
    founded_item = cursor.fetchone()
    if not founded_item:
        connection.close()
        raise HTTPException(status_code=404, detail="Item não encontrado")    
    cursor.execute("DELETE FROM items WHERE name = ?",(item_name,))
    connection.commit()
    connection.close()
    return {"message": "Item deletado do Inventario"}
